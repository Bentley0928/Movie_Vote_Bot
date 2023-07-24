# movie_vote_bot


## This is a telegram bot
![image](https://github.com/weiso131/movie_vote_bot/assets/131360912/d39e74c5-1d79-4040-a0f4-8a285f81e1d9)


## Process Overview:

1. Decide on the movie to watch. 
2. Choose the movie theater to go to.
3. Determine the preferred time slot.

## Command Descriptions

/start,/help : bot send the manual  
/vm + <maximum number of votes>: Generate a movie voting form.  
/vt + <maximum number of votes>: Generate a movie theater voting form (must decide on the movie first and use /next afterward).  
/ti: Generate a time slot voting form (must decide on the movie and movie theater first and use /next) (no vote limit).  
/vote + <option name>: Use the command to vote (can be used with "show all" from the voting form to see all choices at once).  
/sv: Display options with their respective vote counts.  
/search: Display all options voted by the user who called the command.  
/next: Proceed to the next step.  

## Graphical Interface:
"show all": Display all options (for easy copy-pasting).

## bot_example.py
By changing the "TOKEN" to your token and running the program, you can run your movie_vote_bot on your telegram.
![image](https://github.com/weiso131/movie_vote_bot/assets/131360912/24f20a6f-8005-4a1b-8b58-2f6dcc7d3285)





