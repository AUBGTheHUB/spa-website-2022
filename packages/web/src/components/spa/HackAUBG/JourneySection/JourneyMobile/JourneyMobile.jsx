import React from 'react';
import './journey_mobile.css';
import { JourneyStep } from './JourneyStep';

export const JourneyMobile = () => {
    return (
        <div className="journey-mobile-section">
            <div className="journey-mobile-title">
                <h1>
                    The HackAUBG<br></br> Journey
                </h1>
            </div>
            <div className="journey-mobile-content">
                <JourneyStep
                    title={
                        <h2>
                            STEP 1:<br></br> Gather a team and register
                        </h2>
                    }
                    text={
                        <p>
                            Gather your dream team and register in the form
                            below! Don’t forget to create a diverse team, as the
                            best teams usually incorporate programmers, business
                            planners, and designers. The teams should be between
                            3 and 6 people. However, if you have less, don’t
                            worry! Organizers from the Hub will add you to the
                            best suited team for you. Don’t procrastinate
                            registering, because if the registered teams become
                            more than 12, your team will be waitlisted until the
                            very last week before the competition.
                        </p>
                    }
                />
                <JourneyStep
                    title={
                        <h2>
                            STEP 2:<br></br> Meet the Hub and prepare
                        </h2>
                    }
                    text={
                        <p>
                            Right after you click the Register button you will
                            receive an email confirming your place. In the
                            following 48 hours, you will receive another email
                            from us introducing you to your team facilitator - a
                            Hubber who will guide you through everything about
                            HackAUBG 5.0. Pro tip: take a few days to research
                            some hackathon strategies, previous award-winning
                            HackAUBG projects, and brainstorm! After all, you do
                            not want to be unprepared for your chance to bring
                            home the grand prize of 3000 BGN!
                        </p>
                    }
                />
                <JourneyStep
                    title={
                        <h2>
                            STEP 3:<br></br> Get Hackathoning
                        </h2>
                    }
                    text={
                        <p>
                            HackAUBG 5.0 starts on Friday, March 31st. It will
                            be fully on-ground, taking place in the Sports Hall
                            in AUBG&apos;s ABF building. If you do not reside in
                            Blagoevgrad, be sure to make arrangements for your
                            stay here. In case you need help, your Hub
                            facilitator will be more than happy to help you
                            arrange your stay. Below you can check out the
                            HackAUBG 5.0 schedule for all the details. Your
                            facilitator will be checking in with you to make
                            sure you have access to everything needed prior to
                            the event. Once it becomes time for the Opening
                            Ceremony on Friday, March 31st, the theme will be
                            announced. Then it is time to start developing,
                            designing, and strategizing!
                        </p>
                    }
                />
                <JourneyStep
                    title={
                        <h2>
                            STEP 4:<br></br> Present and win
                        </h2>
                    }
                    text={
                        <p>
                            This is the home stretch! You have put in the work
                            and now need to blow the judges away! Your task
                            consists of creating a presentation for your
                            product, as well as a Software Demo. After your
                            presentation, there will be a Q&A session with the
                            panel of judges. The grading criteria for the
                            project and presentation can be found below. Make
                            sure to check it, as it is extremely important! If
                            you have any more questions, check out the FAQ
                            section at the end of the page to learn more!
                        </p>
                    }
                />
            </div>
        </div>
    );
};
