var shellsession_tmLanguage = {name:"shellsession",scopeName:"text.shell-session",patterns:[{match:"(?x) ^ (?: ( (?:\\(\\S+\\)\\s*)? (?: sh\\S*?                       | \\w+\\S+[@:]\\S+(?:\\s+\\S+)? | \\[\\S+?[@:][^\\n]+?\\].*? ) ) \\s* )? ( [>$#%❯➜] | \\p{Greek} ) \\s+ (.*) $",captures:{"1":{name:"entity.other.prompt-prefix.shell-session"},"2":{name:"punctuation.separator.prompt.shell-session"},"3":{name:"source.shell",patterns:[{include:"source.shell"}]}}},{name:"meta.output.shell-session",match:"^.+$"}],fileTypes:["sh-session"]};

export { shellsession_tmLanguage as default };
