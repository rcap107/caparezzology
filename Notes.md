Notes
-----

Source for parsing: 
https://medium.com/@rachit.lsoni/scraping-song-lyrics-a-fun-and-practical-guide-c0b07e8e7312

Genius ID for "Caparezza": 24580

A lot of songs include Caparezza as artist, but he's not the primary artist, 
so I need to filter them out. 

I can't actually scrape from genius because accessing lyrics is behind a captcha, 
and I can't be bothered to figure out how to get around it. 

I found a different website that may let me download the lyrics anyway:
https://www.azlyrics.com/c/caparezza.html

I might still want to use the Genius API to get the annotations and do sentiment
analysis on that to see if it matches the sentiment of the songs themselves. 

The lyrics are not being parsed properly for some reason. 
Needs debugging 

I got IP-banned (whoops). I changed the delay between each song to 10s and added
another delay between all albums of 10 more seconds, and this seems to have 
fixed the issue. 

## Sentiment analysis
https://huggingface.co/docs/transformers/installation

https://huggingface.co/MilaNLProc/feel-it-italian-emotion

https://huggingface.co/MilaNLProc/feel-it-italian-sentiment

