# Awal — Kabyle for the diaspora

## The problem
Kabyle families abroad (France, Canada, US, Belgium…) lose the language in one
or two generations. Kids and young adults understand a little but can't
*speak*, and there is almost no modern, phone-friendly way to learn the
everyday Kabyle that's spoken at home.

## Who pays
**Diaspora adults (20–45)** who want to talk with their parents and
grandparents, and **parents** who want their kids to keep the language. Their
goal is not grammar. They want to say real things to real family members.

## The simplest version someone would pay for
A phone-friendly web app with **short themed lessons of real, everyday
phrases** (greetings, family, at the table, numbers, getting by). Each phrase
comes with a pronunciation hint and a cultural note, you study it with
flashcards, and a quick quiz checks you know it.

- **Free:** the first lesson (Greetings), so people can try it.
- **Paid:** a one-time unlock of all lessons (about €9.99) through a Stripe
  Payment Link. No accounts and no backend in v1.

What makes it worth paying for: native-speaker audio and content from the home
(not textbook Kabyle). The code is the easy part. The **content is the
product**.

## Build steps
1. ✅ **Core app:** lesson list, flashcards, quiz, progress saved on the device.
   Plain HTML/CSS/JS with no build tools, so it opens straight from the file.
2. ✅ **Native audio:** play and slow-play buttons on every phrase, plus a
   recording studio (`#/record`) so a native speaker can record from a phone.
3. **Paywall:** lock lessons 2+ and add an "Unlock" button that goes to a Stripe
   Payment Link, which returns with an unlock code.
4. ✅ **Ship it:** GitHub Pages deploy on every push to `main`, installable
   PWA that works offline (audio is cached after first play). Custom domain
   still to do.
5. **Keep them coming back:** ✅ Duolingo-style path, mixed exercises, XP,
   daily streak. Still to do: daily reminders, a "phrase of the day".

## Out of scope for v1 (on purpose)
Accounts, a backend, AI chat, Tifinagh script, grammar lessons, a native app
store release. Add these only once people are paying.
