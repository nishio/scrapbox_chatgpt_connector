# Scrapbox ChatGPT Connector

The Scrapbox ChatGPT Connector is a simple script for connecting Scrapbox and ChatGPT.

The script is designed so that developers can easily grasp the big picture and customize it to their own needs. Also, the purpose of the project is to show a simple implementation, not to satisfy a wide variety of needs. I encourage everyone to understand the source code and customize it to their own needs.

## For Japanese reader
Visit https://scrapbox.io/villagepump/Scrapbox_ChatGPT_Connector


## How to install

Clone the GitHub repository.

Run the following commands to install the required libraries.

$ pip install -r requirements.txt

## How to use
Obtain an OpenAI API token and save it in an .env file.

```
 OPENAI_API_KEY=sk-...
```

Make index.

$ python make_index.py

It outputs like below:

```
% python make_index.py
 97%|███████████████████████████████████████████████████████████████████████████████████████████████████▉ | 846/872 [07:06<00:10, 2.59 It/s]The server is currently overloaded with other requests. Sorry about that! You can retry your request, or contact us through our help center at help. openai.com if the error persists.
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████| 872/872 [07:45<00:00, 1 .87it/s] 
```

Ask. 

$ python ask.py

It outputs like below:

```
>>>> What is the most important question?
> The most important question is to know ourselves.
```

License
The Scrapbox ChatGPT Connector is distributed under the MIT License. See the LICENSE file for more information.