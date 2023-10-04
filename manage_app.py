#!/usr/bin/env python3
# mypy: ignore-errors
import os
import smtplib as smtp
import subprocess
import threading
import time
from argparse import ArgumentParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict

import requests
import schedule
from dotenv import load_dotenv
from requests import Response

BUILD_RUNNING = threading.Event()
CURRENTLY_BUILDING = threading.Event()
BUILD_FAILED = threading.Event()
lock = threading.Lock()
BUILD_TRY = 0

load_dotenv()

# DEV, PROD, STAGING - this is the identifier of the environment in the emails
ENV = os.environ["DOCK_ENV"]
# e.g. dev.thehub-aubg.com/api/validate or localhost:3000/api/validate
API_URL = os.environ["HUB_API_URL"]
# e.g. dev.thehub-aubg.com or localhost:3000
WEB_URL = os.environ["HUB_WEB_URL"]
PY_API = os.environ["HUB_PY_API_URL"]
SHORTENER = os.environ["HUB_URL_SHORTENER"]
QUESTIONNAIRE = os.environ["HUB_QUESTIONNAIRE"]
# dev.thehub-aubg.com (without http) --> used for cert renewal
CERT_DOMAIN = os.environ["HUB_DOMAIN"]
DISCORD_WH = os.environ["DISCORD_WH"]  # url of webhook (discord channel)
REPO_URL = "https://github.com/AUBGTheHUB/monolith"  # remove last backlash

SERVICES: Dict[str, Dict[str, Any]] = {
    "WEB": {"http_method": "GET", "expected_code": 200, "url": WEB_URL},
    "API": {"http_method": "POST", "expected_code": 400, "url": API_URL},
    "PY-API": {"http_method": "GET", "expected_code": 200, "url": PY_API},
    "URL-SHORTENER": {
        "http_method": "GET", "expected_code": 200,
        "url": SHORTENER,
    },
    "QUESTIONNAIRE": {
        "http_method": "GET", "expected_code": 200,
        "url": QUESTIONNAIRE,
    },
}
args_parser = ArgumentParser(description="CLI args for the script")

args_parser.add_argument(
    "--no-cd", action='store_true',
    help="Disable checking for new changes in the git repo",
)
args_parser.add_argument(
    "--no-renewal", action='store_true',
    help="Disable the renewal of certificates",
)
args_parser.add_argument(
    "--disable-notifications", action="store_true", help="Disables Discord notifications",
)
args_parser.add_argument(
    "--disable-emails", action="store_true",
    help="Disable emails",
)
args = args_parser.parse_args()


class bcolors:
    YELLOW_IN = '\033[33m'
    YELLOW_OUT = '\033[43m'
    RED_IN = '\033[31m'
    CYAN_IN = '\033[93m'
    RED_OUT = '\033[41m'
    OKGREEN = '\033[92m'
    CEND = '\033[0m'


def send_mail(msg):
    if args.disable_emails:
        return

    port = 465  # SSL
    email = os.environ['HUB_MAIL_USERNAME']
    password = os.environ['HUB_MAIL_PASSWORD']

    server = smtp.SMTP_SSL('smtp.gmail.com', port)
    server.login(email, password)
    server.sendmail(email, os.environ['HUB_MAIL_RECEIVER'], msg.as_string())
    server.close()

    print(bcolors.OKGREEN + "An email has been sent!" + bcolors.CEND)


def handle_exception(msg: MIMEMultipart, method: str, url: str, service: str, e: Exception, discord: bool):
    if args.disable_notifications:
        print(
            bcolors.RED_IN + "{}:{} IS DOWN - {}".format(
                ENV,
                service, str(url),
            ) + bcolors.CEND, e,
        )
        return
    if not discord:
        msg.attach(
            MIMEText(
                '<h3>{}: {} Request to {} failed with the following exception: </h3> </p> {}'.format(
                    ENV, method, url,
                    str(e),
                ) + '</p>',
                'html',
            ),
        )
        send_mail(msg)
    else:
        requests.post(
            DISCORD_WH, headers={"Content-Type": "application/x-www-form-urlencoded"}, data={
                "content": f"🏗️: **{ENV}**\n❌: @here {method} Request to {url} failed with the following exception:\n```text\n{str(e)}\n```",
            },
        )


def handle_status_code_exception(
        msg: MIMEMultipart, method: str, url: str, service: str, status_code: int,
        discord: bool,
):
    if args.disable_notifications:
        print(
            bcolors.RED_IN + "{}:{} IS DOWN - {} {}".format(
                ENV,
                service, str(url),
                status_code,
            ) + bcolors.CEND,
        )
        return
    if not discord:
        # send email that the website is down
        msg.attach(
            MIMEText(
                '<h3>{}: {} Request to {} failed with status code {}'.format(
                    ENV, method, url, str(status_code),
                ) + '</h3>', 'html',
            ),
        )
        send_mail(msg)
    else:
        # send discord notification that the website is down
        requests.post(
            DISCORD_WH, headers={"Content-Type": "application/x-www-form-urlencoded"}, data={
                "content": f"🏗️: **{ENV}**\n❌: @here {method} Request to {url} failed with status code: **{str(status_code)}**",
            },
        )


def start_docker_compose():
    # --abort-on-container-exit is not compatible with detached mode
    # therefore check up should be done with requests

    global BUILD_TRY
    msg = MIMEMultipart('alternative')

    # Do not allow new builds to start
    # if a building process is currently running
    if CURRENTLY_BUILDING.is_set():
        return

    CURRENTLY_BUILDING.set()
    with lock:
        if BUILD_TRY == 0:
            BUILD_FAILED.clear()

        BUILD_TRY = BUILD_TRY + 1

    errors: Dict[str, Any] = {}

    def get_current_commit():
        current_commit = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"], check=True, capture_output=True,
        )

        current_commit = subprocess.run(
            ["sed", "1q"], input=current_commit.stdout, capture_output=True,
        )

        return current_commit.stdout.decode('utf-8').strip()

    def get_commit_url():

        hash = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True, text=True,
        )
        return f"{REPO_URL}/commit/{hash.stdout}"

    dc_start = subprocess.run(
        [
            "sudo", "COMPOSE_DOCKER_CLI_BUILD=1", "DOCKER_BUILDKIT=1",
            "docker-compose", "up", "--build", "-d",
        ],
    )

    if dc_start.returncode == 0:
        print()

        time.sleep(10)
        print(bcolors.CYAN_IN + "BUILD HEALTH CHECK:" + bcolors.CEND)
        services_received_status_codes: Dict[str, int] = {}
        for service, details in SERVICES.items():
            status_code = check_service_up(service, details, False)

            services_received_status_codes[service] = status_code

            print()
            time.sleep(10)

        print()
        if check_status_codes(services_received_status_codes):
            print(
                bcolors.OKGREEN +
                f"{ENV} BUILD SUCCESSFUL" + bcolors.CEND,
            )
            BUILD_RUNNING.set()

            msg['Subject'] = f'{ENV}:SPA BUILD SUCCESSFUL'
            msg.attach(
                MIMEText('<h3>All services are working!</h3>', 'html'),
            )
            send_mail(msg)
            if not args.disable_notifications:
                requests.post(
                    DISCORD_WH, headers={
                        "Content-Type": "application/x-www-form-urlencoded",
                    }, data={
                        "content": f"🏗️: **{ENV}**\n🔔: [{get_current_commit()}]({get_commit_url()})\n✅: Successfully Deployed ",
                    },
                )

            # THIS SIGNIFIES THAT A NEW BUILD CAN BE STARTED IF THERE IS AN ERROR
            CURRENTLY_BUILDING.clear()

            # THIS INDICATES THAT THE BUILD HAS BEEN SUCCESSFUL
            BUILD_RUNNING.set()

            with lock:
                BUILD_TRY = 0
            return

        else:
            # docker-compose keeps running when there is a failed container
            errors = services_received_status_codes

    build_err = subprocess.run(
        [
            "sudo", "COMPOSE_DOCKER_CLI_BUILD=1", "DOCKER_BUILDKIT=1",
            "docker-compose", "up", "--build", "-d",
        ],
        capture_output=True,
    )

    errors["BUILD"] = build_err.stderr.decode('utf-8')

    print(bcolors.RED_IN + "BUILD FAILED" + bcolors.CEND)

    msg['Subject'] = f'{ENV}:SPA BUILD FAILED'
    msg.attach(MIMEText('<p>' + str(errors) + '</p>', 'html'))
    send_mail(msg)

    errors["BUILD"] = errors["BUILD"].splitlines()[-10:]

    if BUILD_TRY <= 1:
        if not args.disable_notifications:
            requests.post(
                DISCORD_WH, headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                }, data={
                    "content": f"🏗️: **{ENV}**\n🔔: [{get_current_commit()}]({get_commit_url()})\n❌: @here Build Failed\n```python\n{beautify_errors(errors)}```",
                },
            )

    CURRENTLY_BUILDING.clear()

    with lock:
        if BUILD_TRY >= 2:
            os._exit(1)

    return


def check_status_codes(services_received_status_codes: Dict[str, int]) -> bool:
    """Checks the received status codes from the services against the expected ones
    Returns:
        False if one of the services responded with unexpected status code
        True if all services returned expected status codes
    """
    for service, status_code in services_received_status_codes.items():
        if status_code != SERVICES[service]["expected_code"]:
            return False
    return True


def beautify_errors(errors: Dict[str, Any]) -> str:
    try:
        output_string = ""
        for service, error in errors.items():
            if isinstance(error, int):
                error = f"Status code is: {error}"
            elif isinstance(error, list):
                error = "\n\t".join(error).strip()
            output_string += f"\n{service}:\n\t{error}"
    except Exception as e:
        return str(e)

    return output_string


def stop_docker_compose():
    dc_stop = subprocess.run(["sudo", "docker-compose", "down"])
    BUILD_RUNNING.clear()


def make_service_request(service_details) -> tuple[None, Exception] | tuple[Response, None]:
    try:
        if service_details["http_method"] == "GET":
            response = requests.get(
                service_details["url"], verify=ENV != "LOCAL",
            )
        elif service_details["http_method"] == "POST":
            response = requests.post(
                service_details["url"], verify=ENV != "LOCAL",
            )
        else:
            raise Exception("Invalid method type")
    except Exception as e:
        return None, e

    return response, None


def check_service_up(service: str, details: Dict[str, Any], discord=False) -> Any | None:
    msg = MIMEMultipart('alternative')
    msg['Subject'] = '{}:{} - SERVICE IS DOWN!'.format(
        ENV, service,
    )
    print()
    print(
        bcolors.YELLOW_IN +
        "CHECKING SERVICE {}:{} ".format(
            os.getenv("DOCK_ENV"), service,
        ) + bcolors.CEND,
    )

    response, error = make_service_request(details)
    if error:
        handle_exception(
            msg, details["http_method"], details["url"], service, error, discord,
        )
        return 500
    elif response.status_code != details["expected_code"]:
        handle_status_code_exception(
            msg, details["http_method"], details["url"], service, response.status_code, discord,
        )
        return response.status_code

    print(bcolors.OKGREEN + "Nothing unusual!" + bcolors.CEND)

    return response.status_code


""" definitions of cron jobs """


def cron_local_test():
    # exit if services are currently building
    if CURRENTLY_BUILDING.is_set() or BUILD_FAILED.is_set():
        return

    services_received_status_codes: Dict[str, int] = {}
    for service, details in SERVICES.items():
        status_code = check_service_up(service, details, False)

        services_received_status_codes[service] = status_code
    # build is not running
    if not check_status_codes(services_received_status_codes):
        BUILD_RUNNING.clear()


def cron_git_check_for_updates():
    # only >= 3.7
    remote_update = subprocess.run(
        ['git', 'remote', 'update'], capture_output=True, text=True,
    )
    if remote_update.returncode != 0:
        print("GIT REMOTE UPDATE FAILED: \n{}".format(remote_update.stdout))
        return

    print(remote_update.stdout)

    # only >= 3.7
    status_uno = subprocess.run(
        ['git', 'status'], capture_output=True, text=True,
    )
    if status_uno.returncode != 0:
        print("GIT STATE FAILED: \n{}".format(status_uno.stdout))
        return

    if "Your branch is behind" in status_uno.stdout or "Your branch is ahead" in status_uno.stdout or "diverged" in status_uno.stdout:
        print("BRANCH IS BEHIND!")
        subprocess.run(
            ['git', 'fetch'], capture_output=True, text=True,
        )
        branch_name = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'], capture_output=True, text=True,
        )
        print("Branch name: ", branch_name)
        subprocess.run(
            ['git', 'reset', '--hard', f'origin/{branch_name.stdout}'],
        )
        subprocess.run(
            ['git', 'pull'], capture_output=True, text=True,
        )

        print("STARTING BUILD")
        start_docker_compose()


def cron_self_healing():
    print("BUILD IS RUNNING: {}".format(str(BUILD_RUNNING.is_set())))
    if not BUILD_RUNNING.is_set() and not CURRENTLY_BUILDING.is_set():
        print(bcolors.RED_IN + "WILL TRY TO RECOVER BUILD!" + bcolors.CEND)
        start_docker_compose()


def cron_start_with_new_certs():
    print(
        bcolors.YELLOW_IN +
        "RESTARTING SERVICES SO THAT THE NEW CERTS COULD BE APPLIED" + bcolors.CEND,
    )
    # BUILD_RUNNING.clear()

    # MAKE SURE NEW CERTS ARE INSTALLED
    # Could be done with symbolic links
    pwd = subprocess.check_output(['pwd'])
    pwd = pwd.decode('utf-8').replace('\n', '')
    pwd += '/data/certs/'

    print(bcolors.RED_IN + pwd + bcolors.CEND)

    subprocess.run(['mv', '-f', pwd + 'devenv.crt', pwd + 'devenv_old.crt'])
    subprocess.run(['mv', '-f', pwd + 'devenv.key', pwd + 'devenv_old.key'])

    # we need to unbind the port
    stop_docker_compose()
    CURRENTLY_BUILDING.set()
    subprocess.run(['certbot', 'renew', '--force-renewal'])

    subprocess.run([
        'cp', '/etc/letsencrypt/live/' +
              os.environ["HUB_DOMAIN"] + "/fullchain.pem", pwd + 'devenv.crt',
    ])
    subprocess.run([
        'cp', '/etc/letsencrypt/live/' +
              os.environ["HUB_DOMAIN"] + "/privkey.pem", pwd + 'devenv.key',
    ])

    CURRENTLY_BUILDING.clear()
    start_docker_compose()


""" threading for cron jobs """


def run_thread(job):
    print("\nSTARTING CRON JOB - {}".format(job.__name__))
    thread = threading.Thread(target=job)
    thread.start()
    print()


if args.no_renewal:
    start_docker_compose()
else:
    cron_start_with_new_certs()

schedule.every(1).minutes.do(run_thread, cron_local_test)

schedule.every(200).seconds.do(run_thread, cron_self_healing)
if not args.no_cd:
    schedule.every(60).seconds.do(run_thread, cron_git_check_for_updates)
if not args.no_renewal:
    schedule.every(75).days.do(run_thread, cron_start_with_new_certs)

while True:
    schedule.run_pending()
    time.sleep(1)
