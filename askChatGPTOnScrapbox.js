  scrapbox.PopupMenu.addButton({
    title: "AskChatGPT",
    onClick: (text) => {
      alert(text);
      askChatGPT(text).then((x) => {
        const result = "[ChatGPT.icon]" + x.choices[0].message.content.trim();
        console.log(text + "\n" + result)
        window.chatgpt_result = result;
        alert(text + "\n" + result);
      });
    },
  });
  scrapbox.PopupMenu.addButton({
    title: "PasteChatGPT",
    onClick: (text) => {
      return window.chatgpt_result;
    },
  });
  