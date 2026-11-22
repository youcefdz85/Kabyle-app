import datetime as dt, html
J = ["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"]
M = ["","janv.","févr.","mars","avr.","mai","juin","juil.","août","sept.","oct.","nov.","déc."]
def day(s):
    d = dt.date.fromisoformat(s); return f"<b>{J[d.weekday()].capitalize()}</b><br>{d.day} {M[d.month]}"
# (date, what to post, where/format, caption code, note)
P = [
 ("2026-11-22","<b>Mise en place</b> : créer l'évènement Facebook (bannière), mettre le lien AXS en bio Instagram + Facebook, épingler la carte QR","Facebook + Instagram","—","À faire avant toute publication"),
 ("2026-11-23","<b>Teaser 1</b> « Alluh Alluh »","Reel 9:16 + fil 4:5","A","Partager aussi dans les groupes WhatsApp (1:1)"),
 ("2026-11-25","<b>Reel Keswick Theatre</b> (votre invitation)","Reel 9:16","B","Le plus personnel : à épingler en haut du profil"),
 ("2026-11-27","<b>Pub 15 s</b> — Black Friday : « offrez une place »","Reel + Story","C","Idée cadeau des fêtes"),
 ("2026-11-29","<b>Interview du sponsor</b> Hanane's Signature Patisserie (vidéo longue)","Facebook + YouTube","D","Taguer @Hanane's ; elle repartage"),
 ("2026-12-02","<b>Teaser 2</b> « Asderfef »","Reel 9:16 + fil 4:5","A","Groupes WhatsApp (1:1)"),
 ("2026-12-05","<b>Reel bonus n°1</b> (créé par votre vidéaste)","Reel 9:16","E",""),
 ("2026-12-08","<b>Extrait court du sponsor</b> (30–60 s) + carte QR en story","Reel + Story","D","Remercier le sponsor"),
 ("2026-12-11","<b>Compte à rebours J-30</b>","Story 9:16 + post 4:5","F","Fichiers datés « 2026-12-11 »"),
 ("2026-12-14","<b>Reel bonus n°2</b>","Reel 9:16","E",""),
 ("2026-12-17","<b>Reel Keswick</b> en version Facebook (re-partage) + carte QR","Facebook + groupes","B","Nouveau public"),
 ("2026-12-20","<b>Compte à rebours J-21</b>","Story + post 4:5","F",""),
 ("2026-12-23","<b>Pub 15 s</b> — Noël : « offrez une place pour Yennayer »","Reel + Story","C","Idée cadeau"),
 ("2026-12-27","<b>Compte à rebours J-14</b>","Story + post 4:5","F",""),
 ("2026-12-29","<b>Reel bonus n°3</b>","Reel 9:16","E",""),
 ("2027-01-01","<b>Teaser 3</b> « Yennayer » + vœux de bonne année","Reel 9:16 + fil 4:5","G","Fort potentiel de partage"),
 ("2027-01-03","<b>Compte à rebours J-7</b>","Story + post 4:5","F","Doubler le budget pub à partir d'aujourd'hui"),
 ("2027-01-05","<b>Interview du sponsor</b> (re-partage) ou nouveau Reel","Reel / Facebook","D",""),
 ("2027-01-07","<b>Compte à rebours J-3</b>","Story + post 4:5","F","Infos pratiques : portes, parking"),
 ("2027-01-09","<b>J-1 « TOMORROW »</b>","Story + post 4:5","F","Stories de l'arrivée de l'artiste si possible"),
 ("2027-01-10","<b>« TONIGHT »</b> + stories en direct pendant la soirée","Story + post","H","Après le concert : « Merci Philadelphia ! »"),
]
rows = "\n".join(f"<tr><td class='d'>{day(a)}</td><td>{b}</td><td class='f'>{c}</td><td class='c'>{e}</td><td class='n'>{n}</td><td class='x'><span class='cb'></span></td></tr>" for a,b,c,e,n in P)
open("calendrier_rows.html","w").write(rows)
