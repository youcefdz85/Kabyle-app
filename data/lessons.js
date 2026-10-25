// Lesson content. Edit freely — each phrase needs: id, kab (Kabyle), and a
// translation for every app language: en, fr, es, de, ar.
// "id" names the recording: audio/<lessonId>-<id>.mp3 (or .m4a/.webm/.ogg).
// Keep ids unique within a lesson and don't change them once audio is recorded.
// Optional: say (English-style pronunciation hint, shown in English only),
// note ({ en, fr, es, de, ar }: usage / culture).
// Lesson titles are { en, fr, es, de, ar } too.
// Picture cards are drawn in pictures.js, keyed by "<lessonId>-<phraseId>".
// "free: true" lessons are available without unlocking (paywall comes in step 3).
// Run `node tests/check-content.js` after editing to catch missing translations.
// ⚠️ Please have a native speaker review every phrase before selling.
window.LESSONS = [
  {
    id: "greetings",
    title: { en: "Greetings", fr: "Salutations", es: "Saludos", de: "Begrüßungen", ar: "التحيات" },
    emoji: "👋",
    free: true,
    phrases: [
      { id: "azul", kab: "Azul", say: "ah-ZOOL",
        en: "Hello", fr: "Bonjour / Salut", es: "Hola", de: "Hallo", ar: "مرحبًا",
        note: {
          en: "The universal Amazigh greeting — works with anyone.",
          fr: "La salutation amazighe universelle — elle marche avec tout le monde.",
          es: "El saludo amazigh universal: sirve con cualquiera.",
          de: "Der universelle amazighische Gruß – passt bei allen.",
          ar: "التحية الأمازيغية الجامعة — تصلح مع الجميع."
        } },
      { id: "amek-telled", kab: "Amek telliḍ?", say: "ah-MEK tel-LEED",
        en: "How are you?", fr: "Comment vas-tu ?", es: "¿Cómo estás?", de: "Wie geht's dir?", ar: "كيف حالك؟",
        note: {
          en: "Same form for a man or a woman.",
          fr: "Même forme pour un homme ou une femme.",
          es: "La misma forma para un hombre o una mujer.",
          de: "Gleiche Form für Mann und Frau.",
          ar: "الصيغة نفسها للرجل والمرأة."
        } },
      { id: "labas-tanemmirt", kab: "Labas, tanemmirt", say: "la-BAS, ta-nem-MEERT",
        en: "Fine, thank you", fr: "Bien, merci", es: "Bien, gracias", de: "Gut, danke", ar: "بخير، شكرًا" },
      { id: "tanemmirt", kab: "Tanemmirt", say: "ta-nem-MEERT",
        en: "Thank you", fr: "Merci", es: "Gracias", de: "Danke", ar: "شكرًا" },
      { id: "ansuf", kab: "Ansuf yis-k / yis-m", say: "an-SOOF yis-k / yis-m",
        en: "Welcome (to a man / a woman)",
        fr: "Bienvenue (à un homme / à une femme)",
        es: "Bienvenido / Bienvenida (a un hombre / a una mujer)",
        de: "Willkommen (zu einem Mann / einer Frau)", ar: "أهلًا وسهلًا (لرجل / لامرأة)" },
      { id: "sbah-lxir", kab: "Sbaḥ lxir", say: "sbah l-KHEER",
        en: "Good morning", fr: "Bonjour (le matin)", es: "Buenos días", de: "Guten Morgen", ar: "صباح الخير",
        note: {
          en: "The 'x' is a throaty sound, like Spanish 'j'.",
          fr: "Le « x » se prononce du fond de la gorge, comme la jota espagnole.",
          es: "La «x» es un sonido gutural, como la «j» española.",
          de: "Das „x“ ist ein Kehllaut wie das „ch“ in „Bach“.",
          ar: "حرف «x» يُنطق مثل الخاء (خ)."
        } },
      { id: "ar-tufat", kab: "Ar tufat", say: "ar too-FAT",
        en: "See you tomorrow / Goodbye", fr: "À demain / Au revoir", es: "Hasta mañana / Adiós", de: "Bis morgen / Tschüss", ar: "إلى الغد / مع السلامة" },
      { id: "ar-timlilit", kab: "Ar timlilit", say: "ar tim-lee-LEET",
        en: "See you soon", fr: "À bientôt", es: "Hasta pronto", de: "Bis bald", ar: "إلى اللقاء قريبًا",
        note: {
          en: "Literally 'until the meeting'.",
          fr: "Littéralement « jusqu'à la rencontre ».",
          es: "Literalmente «hasta el encuentro».",
          de: "Wörtlich „bis zum Treffen“.",
          ar: "حرفيًا: «إلى اللقاء»."
        } }
    ]
  },
  {
    id: "family",
    title: { en: "Family", fr: "Famille", es: "Familia", de: "Familie", ar: "العائلة" },
    emoji: "👨‍👩‍👧",
    phrases: [
      { id: "yemma", kab: "Yemma", say: "YEM-ma",
        en: "Mom / my mother", fr: "Maman / ma mère", es: "Mamá / mi madre", de: "Mama / meine Mutter", ar: "أمي / ماما" },
      { id: "vava", kab: "Vava", say: "VA-va",
        en: "Dad / my father", fr: "Papa / mon père", es: "Papá / mi padre", de: "Papa / mein Vater", ar: "أبي / بابا" },
      { id: "jeddi", kab: "Jeddi", say: "JED-dee",
        en: "Grandpa", fr: "Grand-père", es: "Abuelo", de: "Opa", ar: "جدي" },
      { id: "setti", kab: "Setti / Jida", say: "SET-tee / JEE-da",
        en: "Grandma", fr: "Grand-mère", es: "Abuela", de: "Oma", ar: "جدتي",
        note: {
          en: "Both are used: say the one your family says.",
          fr: "Les deux se disent : utilise celui de ta famille.",
          es: "Se usan los dos: di el que se dice en tu familia.",
          de: "Beides ist üblich – sag das, was deine Familie sagt.",
          ar: "الكلمتان مستعملتان: قل ما تقوله عائلتك."
        } },
      { id: "gma", kab: "Gma", say: "g-MA",
        en: "My brother", fr: "Mon frère", es: "Mi hermano", de: "Mein Bruder", ar: "أخي" },
      { id: "weltma", kab: "Weltma", say: "WELT-ma",
        en: "My sister", fr: "Ma sœur", es: "Mi hermana", de: "Meine Schwester", ar: "أختي" },
      { id: "mmi", kab: "Mmi", say: "m-MEE",
        en: "My son", fr: "Mon fils", es: "Mi hijo", de: "Mein Sohn", ar: "ابني" },
      { id: "yelli", kab: "Yelli", say: "YEL-lee",
        en: "My daughter", fr: "Ma fille", es: "Mi hija", de: "Meine Tochter", ar: "ابنتي" },
      { id: "hemmlegh-k", kab: "Ḥemmleɣ-k", say: "HEM-legh-k",
        en: "I love you (to a man)", fr: "Je t'aime (à un homme)", es: "Te quiero (a un hombre)", de: "Ich liebe dich (zu einem Mann)", ar: "أحبك (لرجل)",
        note: {
          en: "'ɣ' is a gargled r, like the French 'r'.",
          fr: "Le « ɣ » se prononce comme le « r » français.",
          es: "La «ɣ» es una r gutural, como la «r» francesa.",
          de: "Das „ɣ“ ist ein gegurgeltes R, wie das deutsche Zäpfchen-R.",
          ar: "حرف «ɣ» يُنطق مثل الغين (غ)."
        } },
      { id: "hemmlegh-kem", kab: "Ḥemmleɣ-kem", say: "HEM-legh-kem",
        en: "I love you (to a woman)", fr: "Je t'aime (à une femme)", es: "Te quiero (a una mujer)", de: "Ich liebe dich (zu einer Frau)", ar: "أحبك (لامرأة)" }
    ]
  },
  {
    id: "table",
    title: { en: "At the table", fr: "À table", es: "En la mesa", de: "Am Tisch", ar: "على المائدة" },
    emoji: "🍲",
    phrases: [
      { id: "aman", kab: "Aman", say: "a-MAN",
        en: "Water", fr: "De l'eau", es: "Agua", de: "Wasser", ar: "ماء" },
      { id: "aghrum", kab: "Aɣrum", say: "a-GHROOM",
        en: "Bread", fr: "Du pain", es: "Pan", de: "Brot", ar: "خبز" },
      { id: "seksu", kab: "Seksu", say: "SEK-soo",
        en: "Couscous", fr: "Couscous", es: "Cuscús", de: "Couscous", ar: "كسكس",
        note: {
          en: "The heart of every Kabyle family meal.",
          fr: "Le cœur de chaque repas de famille kabyle.",
          es: "El corazón de toda comida familiar cabila.",
          de: "Das Herzstück jedes kabylischen Familienessens.",
          ar: "قلب كل وجبة عائلية قبائلية."
        } },
      { id: "tiremt", kab: "Tiremt", say: "tee-REMT",
        en: "A meal", fr: "Un repas", es: "Una comida", de: "Eine Mahlzeit", ar: "وجبة" },
      { id: "fell-i-laz", kab: "Fell-i laẓ", say: "fel-LEE laz",
        en: "I'm hungry", fr: "J'ai faim", es: "Tengo hambre", de: "Ich habe Hunger", ar: "أنا جائع" },
      { id: "yelha-nezzeh", kab: "Yelha nezzeh!", say: "YEL-ha nez-ZEH",
        en: "It's very good!", fr: "C'est très bon !", es: "¡Está muy bueno!", de: "Es ist sehr gut!", ar: "إنه لذيذ جدًا!",
        note: {
          en: "Say this to whoever cooked — it will make their day.",
          fr: "Dis-le à la personne qui a cuisiné — ça lui fera plaisir.",
          es: "Díselo a quien cocinó: le alegrará el día.",
          de: "Sag das zu der Person, die gekocht hat – das freut sie sehr.",
          ar: "قلها لمن طبخ — ستُسعده كثيرًا."
        } },
      { id: "sahha", kab: "Ṣaḥḥa", say: "SAH-ha",
        en: "Thanks / Bon appétit / Cheers", fr: "Merci / Bon appétit / Santé",
        es: "Gracias / Buen provecho / Salud", de: "Danke / Guten Appetit / Prost", ar: "شكرًا / بالهناء / بالصحة",
        note: {
          en: "Literally 'health'. Used after a meal and in many other situations.",
          fr: "Littéralement « santé ». S'utilise après un repas et dans bien d'autres situations.",
          es: "Literalmente «salud». Se usa después de comer y en muchas otras situaciones.",
          de: "Wörtlich „Gesundheit“. Sagt man nach dem Essen und in vielen anderen Situationen.",
          ar: "حرفيًا: «الصحة». تُقال بعد الأكل وفي مواقف كثيرة أخرى."
        } }
    ]
  },
  {
    id: "numbers",
    title: { en: "Numbers 1–10", fr: "Nombres de 1 à 10", es: "Números del 1 al 10", de: "Zahlen 1–10", ar: "الأعداد من 1 إلى 10" },
    emoji: "🔢",
    phrases: [
      { id: "1", kab: "Yiwen", say: "yi-WEN", en: "One", fr: "Un", es: "Uno", de: "Eins", ar: "واحد" },
      { id: "2", kab: "Sin", say: "seen", en: "Two", fr: "Deux", es: "Dos", de: "Zwei", ar: "اثنان" },
      { id: "3", kab: "Kraḍ", say: "krad", en: "Three", fr: "Trois", es: "Tres", de: "Drei", ar: "ثلاثة" },
      { id: "4", kab: "Kkuẓ", say: "kkooz", en: "Four", fr: "Quatre", es: "Cuatro", de: "Vier", ar: "أربعة" },
      { id: "5", kab: "Semmus", say: "sem-MOOS", en: "Five", fr: "Cinq", es: "Cinco", de: "Fünf", ar: "خمسة" },
      { id: "6", kab: "Sḍis", say: "sdees", en: "Six", fr: "Six", es: "Seis", de: "Sechs", ar: "ستة" },
      { id: "7", kab: "Sa", say: "sa", en: "Seven", fr: "Sept", es: "Siete", de: "Sieben", ar: "سبعة" },
      { id: "8", kab: "Tam", say: "tam", en: "Eight", fr: "Huit", es: "Ocho", de: "Acht", ar: "ثمانية" },
      { id: "9", kab: "Tẓa", say: "tza", en: "Nine", fr: "Neuf", es: "Nueve", de: "Neun", ar: "تسعة" },
      { id: "10", kab: "Mraw", say: "mraw", en: "Ten", fr: "Dix", es: "Diez", de: "Zehn", ar: "عشرة" }
    ]
  },
  {
    id: "getting-by",
    title: { en: "Getting by", fr: "Se débrouiller", es: "Defenderse", de: "Zurechtkommen", ar: "التدبّر" },
    emoji: "💬",
    phrases: [
      { id: "ih", kab: "Ih", say: "eeh", en: "Yes", fr: "Oui", es: "Sí", de: "Ja", ar: "نعم" },
      { id: "ala", kab: "Ala", say: "a-LA", en: "No", fr: "Non", es: "No", de: "Nein", ar: "لا" },
      { id: "ma-ulac-aghilif", kab: "Ma ulac aɣilif", say: "ma oo-LASH a-ghee-LEEF",
        en: "Please / Excuse me", fr: "S'il te plaît / Excuse-moi", es: "Por favor / Disculpa", de: "Bitte / Entschuldigung", ar: "من فضلك / عذرًا" },
      { id: "ur-fhimegh-ara", kab: "Ur fhimeɣ ara", say: "oor f-HEE-megh a-RA",
        en: "I don't understand", fr: "Je ne comprends pas", es: "No entiendo", de: "Ich verstehe nicht", ar: "لم أفهم" },
      { id: "awed", kab: "Ɛawed, ma ulac aɣilif", say: "AA-wed, ma oo-LASH a-ghee-LEEF",
        en: "Repeat, please", fr: "Répète, s'il te plaît", es: "Repite, por favor", de: "Wiederhol bitte", ar: "أعد من فضلك",
        note: {
          en: "'Ɛ' is a deep sound from the throat, like Arabic ع.",
          fr: "Le « ɛ » est un son profond de la gorge, comme le ع arabe.",
          es: "La «ɛ» es un sonido profundo de la garganta, como la ع árabe.",
          de: "Das „ɛ“ ist ein tiefer Kehllaut wie das arabische ع.",
          ar: "حرف «ɛ» يُنطق مثل العين (ع)."
        } },
      { id: "s-ttawil", kab: "Ttxil-k, s ttawil", say: "t-KHEEL-k, s ta-WEEL",
        en: "Please, slowly (to a man)", fr: "S'il te plaît, doucement (à un homme)",
        es: "Por favor, despacio (a un hombre)", de: "Bitte langsam (zu einem Mann)", ar: "من فضلك، ببطء (لرجل)" },
      { id: "isem-iw", kab: "Isem-iw …", say: "ee-SEM-iw",
        en: "My name is …", fr: "Je m'appelle …", es: "Me llamo …", de: "Ich heiße …", ar: "اسمي …" },
      { id: "nekk-seg", kab: "Nekk seg Tizi Wezzu", say: "nekk seg TEE-zee WEZ-zoo",
        en: "I'm from Tizi Ouzou", fr: "Je viens de Tizi Ouzou", es: "Soy de Tizi Ouzou", de: "Ich komme aus Tizi Ouzou", ar: "أنا من تيزي وزو",
        note: {
          en: "Swap in your family's village or town.",
          fr: "Remplace par le village ou la ville de ta famille.",
          es: "Cámbialo por el pueblo o la ciudad de tu familia.",
          de: "Setz das Dorf oder die Stadt deiner Familie ein.",
          ar: "ضع اسم قرية عائلتك أو مدينتها."
        } }
    ]
  }
];
