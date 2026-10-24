// Lesson content. Edit freely — each phrase needs: id, kab (Kabyle), en (English).
// "id" names the recording: audio/<lessonId>-<id>.mp3 (or .m4a/.webm/.ogg).
// Keep ids unique within a lesson and don't change them once audio is recorded.
// Optional: say (pronunciation hint), note (usage / culture).
// "free: true" lessons are available without unlocking (paywall comes in step 3).
// ⚠️ Please have a native speaker review every phrase before selling.
window.LESSONS = [
  {
    id: "greetings",
    title: "Greetings",
    emoji: "👋",
    free: true,
    phrases: [
      { id: "azul", kab: "Azul", en: "Hello", say: "ah-ZOOL", note: "The universal Amazigh greeting — works with anyone." },
      { id: "amek-telled", kab: "Amek telliḍ?", en: "How are you?", say: "ah-MEK tel-LEED", note: "Same form for a man or a woman." },
      { id: "labas-tanemmirt", kab: "Labas, tanemmirt", en: "Fine, thank you", say: "la-BAS, ta-nem-MEERT" },
      { id: "tanemmirt", kab: "Tanemmirt", en: "Thank you", say: "ta-nem-MEERT" },
      { id: "ansuf", kab: "Ansuf yis-k / yis-m", en: "Welcome (to a man / a woman)", say: "an-SOOF yis-k / yis-m" },
      { id: "sbah-lxir", kab: "Sbaḥ lxir", en: "Good morning", say: "sbah l-KHEER", note: "The 'x' is a throaty sound, like Spanish 'j'." },
      { id: "ar-tufat", kab: "Ar tufat", en: "See you tomorrow / Goodbye", say: "ar too-FAT" },
      { id: "ar-timlilit", kab: "Ar timlilit", en: "See you soon", say: "ar tim-lee-LEET", note: "Literally 'until the meeting'." }
    ]
  },
  {
    id: "family",
    title: "Family",
    emoji: "👨‍👩‍👧",
    phrases: [
      { id: "yemma", kab: "Yemma", en: "Mom / my mother", say: "YEM-ma" },
      { id: "baba", kab: "Baba", en: "Dad / my father", say: "BA-ba" },
      { id: "jeddi", kab: "Jeddi", en: "Grandpa", say: "JED-dee" },
      { id: "nanna", kab: "Nanna", en: "Grandma (also: elder sister)", say: "NAN-na", note: "Some families say 'Setti' or 'Jida' instead." },
      { id: "gma", kab: "Gma", en: "My brother", say: "g-MA" },
      { id: "weltma", kab: "Weltma", en: "My sister", say: "WELT-ma" },
      { id: "mmi", kab: "Mmi", en: "My son", say: "m-MEE" },
      { id: "yelli", kab: "Yelli", en: "My daughter", say: "YEL-lee" },
      { id: "hemmlegh-k", kab: "Ḥemmleɣ-k", en: "I love you (to a man)", say: "HEM-legh-k", note: "'ɣ' is a gargled r, like the French 'r'." },
      { id: "hemmlegh-kem", kab: "Ḥemmleɣ-kem", en: "I love you (to a woman)", say: "HEM-legh-kem" }
    ]
  },
  {
    id: "table",
    title: "At the table",
    emoji: "🍲",
    phrases: [
      { id: "aman", kab: "Aman", en: "Water", say: "a-MAN" },
      { id: "aghrum", kab: "Aɣrum", en: "Bread", say: "a-GHROOM" },
      { id: "seksu", kab: "Seksu", en: "Couscous", say: "SEK-soo", note: "The heart of every Kabyle family meal." },
      { id: "tiremt", kab: "Tiremt", en: "A meal", say: "tee-REMT" },
      { id: "fell-i-laz", kab: "Fell-i laẓ", en: "I'm hungry", say: "fel-LEE laz" },
      { id: "yelha-nezzeh", kab: "Yelha nezzeh!", en: "It's very good!", say: "YEL-ha nez-ZEH", note: "Say this to whoever cooked — it will make their day." },
      { id: "sahha", kab: "Ṣaḥḥa", en: "Thanks / Bon appétit / Cheers", say: "SAH-ha", note: "Literally 'health'. Used after a meal and in many other situations." }
    ]
  },
  {
    id: "numbers",
    title: "Numbers 1–10",
    emoji: "🔢",
    phrases: [
      { id: "1", kab: "Yiwen", en: "One", say: "yi-WEN" },
      { id: "2", kab: "Sin", en: "Two", say: "seen" },
      { id: "3", kab: "Kraḍ", en: "Three", say: "krad" },
      { id: "4", kab: "Kkuẓ", en: "Four", say: "kkooz" },
      { id: "5", kab: "Semmus", en: "Five", say: "sem-MOOS" },
      { id: "6", kab: "Sḍis", en: "Six", say: "sdees" },
      { id: "7", kab: "Sa", en: "Seven", say: "sa" },
      { id: "8", kab: "Tam", en: "Eight", say: "tam" },
      { id: "9", kab: "Tẓa", en: "Nine", say: "tza" },
      { id: "10", kab: "Mraw", en: "Ten", say: "mraw" }
    ]
  },
  {
    id: "getting-by",
    title: "Getting by",
    emoji: "💬",
    phrases: [
      { id: "ih", kab: "Ih", en: "Yes", say: "eeh" },
      { id: "ala", kab: "Ala", en: "No", say: "a-LA" },
      { id: "ma-ulac-aghilif", kab: "Ma ulac aɣilif", en: "Please / Excuse me", say: "ma oo-LASH a-ghee-LEEF" },
      { id: "ur-fhimegh-ara", kab: "Ur fhimeɣ ara", en: "I don't understand", say: "oor f-HEE-megh a-RA" },
      { id: "awed", kab: "Ɛawed, ma ulac aɣilif", en: "Repeat, please", say: "AA-wed, ma oo-LASH a-ghee-LEEF", note: "'Ɛ' is a deep sound from the throat, like Arabic ع." },
      { id: "s-ttawil", kab: "Ttxil-k, s ttawil", en: "Please, slowly (to a man)", say: "t-KHEEL-k, s ta-WEEL" },
      { id: "isem-iw", kab: "Isem-iw …", en: "My name is …", say: "ee-SEM-iw" },
      { id: "nekk-seg", kab: "Nekk seg Tizi Wezzu", en: "I'm from Tizi Ouzou", say: "nekk seg TEE-zee WEZ-zoo", note: "Swap in your family's village or town." }
    ]
  }
];
