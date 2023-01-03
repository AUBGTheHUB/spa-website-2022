#!/bin/bash
current_directory=${PWD##*/} 
if [[ $current_directory != "spa-website-2022" ]]
then
    echo "Run this script from the $(gum style --foreground 212 "ROOT DIRECTORY") of the SPA project"
    exit 1
fi

gum style --border normal --margin "1" --padding "1 2" --border-foreground 212 "Hello, there! Welcome to The Hub's $(gum style --foreground 212 'SPA project')."

echo -e "What would you like to do?"

START="Develop"
DEPLOY="Deploy"

ACTIONS=$(gum choose --cursor-prefix "[ ] " --selected-prefix "[✓] " --no-limit "$START" "$DEPLOY" )

if [ $ACTIONS == $START ]; then
    clear
    echo -e "What instance do you want to spin up?"

    LOCAL_CLIENT="Client (requests towards local api)"
    DEPLOYED_CLIENT="Client (requests towards deployed api)"
    LOCAL_API="Run Api"
    ACTIONS=$(gum choose --cursor-prefix "[ ] " --selected-prefix "[✓] " --no-limit "$LOCAL_CLIENT" "$DEPLOYED_CLIENT" "$LOCAL_API")

    clear

    if [ "$ACTIONS" == "$LOCAL_CLIENT" ]; then 
        make run-web
    elif [ "$ACTIONS" == "$DEPLOYED_CLIENT" ]; then
        make run-dev
    elif [ "$ACTIONS" == "$LOCAL_API" ]; then
        make run-api
    fi

elif [ "$ACTIONS" == "$DEPLOY" ]; then
    echo $(gum style --foreground 212 "NOT SUPPORTED, YET!")
fi
