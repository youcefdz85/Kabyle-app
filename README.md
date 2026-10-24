# Awal: learn Kabyle

A simple, phone-friendly app that helps the Kabyle diaspora learn the everyday
Kabyle spoken at home, through short themed lessons, flashcards and quizzes.

See [PLAN.md](PLAN.md) for the product plan and the build steps.

## Run it
Open `index.html` in a browser. There are no build steps and nothing to install.

## Edit the content
All phrases are in [`data/lessons.js`](data/lessons.js). Each phrase has
`kab`, `en`, and optional `say` (pronunciation) and `note` (culture or usage).

## Add native-speaker audio
Open `index.html#/record` to use the recording studio. Record each phrase,
press **Save file**, and put the saved files in the `audio/` folder. See
[`audio/README.md`](audio/README.md) for details. Phrases without a recording
show "No recording yet."

The recording studio needs microphone access, so open it from a web address
(`https://` or `localhost`), not by double-clicking the file. For example, run
`python3 -m http.server` in this folder and visit
`http://localhost:8000/#/record`.
