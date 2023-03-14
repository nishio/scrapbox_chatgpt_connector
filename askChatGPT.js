// ==UserScript==
// @name         New Userscript
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       You
// @match        https://scrapbox.io/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=scrapbox.io
// @grant        GM_xmlhttpRequest
// ==/UserScript==

unsafeWindow.askChatGPT = async (
  text,
  { temperature = 0.7, max_tokens = 500 } = {}
) => {
  const headers = {
    "Content-Type": "application/json",
    Authorization: "Bearer " + localStorage.getItem("OPENAI_KEY"),
  };
  const data = JSON.stringify({
    temperature,
    max_tokens,
    model: "gpt-3.5-turbo",
    messages: [{ role: "user", content: text }],
  });

  return await new Promise((resolve, reject) =>
    GM_xmlhttpRequest({
      method: "POST",
      url: "https://api.openai.com/v1/chat/completions",
      data: requestOptions.data,
      headers: requestOptions.headers,
      onload: ({ response }) =>
        resolve({
          ...response,
        }),
      responseType: "json",
      onerror: (e) => reject(e),
    })
  );
};
