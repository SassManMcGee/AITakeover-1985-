import { fetch } from 'wix-fetch';

export async function initiate_gpt(text, user) {
    const url = '"INSERT NGROK URL"/request/';

    return fetch(url + text, {
        method: "get",
        headers:{ "ngrok-skip-browser-warning": "69420", },
    })
      .then((Response) => { return Response.json(); })
      .then((data) => { return data; })
      .catch((err) => { return err; });
}

export async function ask_gpt(text, user) {
    const url = '"INSERT NGROK URL"/request/';

    return fetch(url + text, {
        method: "get",
        headers:{ "ngrok-skip-browser-warning": "69420", },
    })
      .then((Response) => { return Response.json(); })
      .then((data) => { return data; })
      .catch((err) => { return err; });
}