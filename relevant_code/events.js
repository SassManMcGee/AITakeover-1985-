import { initiate_gpt, ask_gpt } from 'backend/openai.js';
import wixChatBackend from 'wix-chat-backend';
import wixData from 'wix-data';

export function wixChat_onMessage(event) {
  if (event.direction === 'VisitorToBusiness') {
    console.log('Chat was commenced');
    commence(event);
  }
}

const commence = (event) => {
  wixData.query('gpt_chat').eq('channelId', event.channelId).find()
  .then(async (res) => {
    console.log('Query completed');
    if (res.items.length > 0) {
      // Existing Chat
      let gpt_res = await initiate_gpt(event.payload.text, event.sender.id);
      gpt_response(gpt_res, event.channelId, event.payload.text);
    } else {
      // New Chat
      let obj = {
        channelId: event.channelId,
        userId: event.sender.id
      };
      wixData.insert('gpt_chat', obj);
      let gpt_res2 = await ask_gpt(event.payload.text, event.sender.id);
      gpt_response(gpt_res2, event.channelId, event.payload.text);
    }
  });
};

const gpt_response = (gpt, chid, prev) => {
  let obj = {
    "messageText": gpt.Response,
    "channelId": chid,
    "sendAsVisitor": false
  };
  console.log(obj);
  wixChatBackend.sendMessage(obj)
  .then(() => {
    console.log("Chat message sent");
  })
  .catch((error) => {
    console.log(error);
  });
};