"use strict";
(() => {
  const en = {
    "Writer · Κείμενο":"Writer · Text", "Κείμενο":"Text", "Το προσχέδιο θα εμφανιστεί εδώ.":"The draft will appear here.", "Εγκρίνω το κείμενο":"Approve text", "Η μετάφρασή σου":"Your translation", "Μεταφρασμένο κείμενο":"Translated text", "Η μετάφραση θα εμφανιστεί εδώ.":"The translation will appear here.",
    "Μοντέλο Writer / Ollama":"Writer / Ollama model", "Μοντέλο μετάφρασης / Ollama":"Translation / Ollama model", "Αναζήτηση μοντέλων…":"Searching for models…", "Επίλεξε μοντέλο":"Select a model", "Ανανέωση":"Refresh", "Διαχείριση μοντέλων":"Manage models", "Φωτεινό":"Light", "Σκοτεινό":"Dark", "Βοήθεια":"Help", "Ρυθμίσεις":"Settings", "Αλλαγή γλώσσας και εμφάνισης από τα κουμπιά στο επάνω μέρος της εφαρμογής.":"Change language and appearance using the buttons at the top of the application.", "Οι προτιμήσεις διατηρούνται στον browser για την τρέχουσα τοπική διεύθυνση. Τα κείμενα δεν αποθηκεύονται αυτόματα.":"Preferences are kept in the browser for this local address. Texts are not saved automatically.", "Πληροφορίες":"Info", "Τερματισμός εφαρμογής":"Stop application", "Χώρος εργασίας":"Workspace",
    "Σημειώσεις":"Notes", "Η ΑΦΕΤΗΡΙΑ ΣΟΥ":"YOUR STARTING POINT", "Οι ιδέες σου":"Your ideas", "Γράψε ή επικόλλησε ελληνικές σημειώσεις και bullet points.":"Write or paste Greek notes and bullet points.", "ΠΡΩΤΟΤΥΠΟ":"ORIGINAL", "Οι σημειώσεις σου":"Your notes", "Ελληνικά":"Greek", "Οι σημειώσεις σου παραμένουν ξεχωριστές από το αποτέλεσμα.":"Your notes remain separate from the result.", "Δημιουργία ελληνικού κειμένου":"Generate Greek text", "Αποθήκευση σημειώσεων":"Save notes",
    "Writer · Ελληνικό κείμενο":"Writer · Greek text", "ΔΗΜΙΟΥΡΓΙΑ & ΕΛΕΓΧΟΣ":"CREATE & REVIEW", "Από τις ιδέες σε κείμενο":"From ideas to text", "Δημιούργησε ένα προσχέδιο και διαμόρφωσέ το όπως θέλεις.":"Create a draft and edit it as you wish.", "Μηχανή συγγραφής":"Writing engine", "Το Ollama χρησιμοποιεί το μοντέλο που επέλεξες σε αυτή τη στήλη.":"Ollama uses the model selected in this column.", "ΠΡΟΣΧΕΔΙΟ":"DRAFT", "Ελληνικό κείμενο":"Greek text", "Έλεγξε το νόημα και το προσωπικό σου ύφος πριν συνεχίσεις.":"Review the meaning and your personal style before continuing.", "Εγκρίνω το ελληνικό κείμενο":"Approve Greek text", "Αποθήκευση προσχεδίου":"Save draft", "Το προσχέδιο χρειάζεται τον έλεγχό σου.":"Please review the draft.",
    "Translator · Μετάφραση":"Translator · Translation", "ΜΕΤΑΦΡΑΣΗ & ΕΓΚΡΙΣΗ":"TRANSLATE & APPROVE", "Το κείμενό σου στα αγγλικά":"Your text in English", "Το κείμενό σου στα ελληνικά":"Your text in Greek", "Έλεγξε τη μετάφραση και κράτησε το τελικό αποτέλεσμα.":"Review the translation and save the final result.", "Κατεύθυνση μετάφρασης":"Translation direction", "Ελληνικά → Αγγλικά":"Greek → English", "Αγγλικά → Ελληνικά":"English → Greek", "Αγγλικό κείμενο προς μετάφραση":"English text to translate", "Εγκρίνω το αγγλικό κείμενο":"Approve English text", "Το αγγλικό κείμενο χρειάζεται τον έλεγχό σου.":"Please review the English text.", "Μηχανή μετάφρασης":"Translation engine", "ΜΕΤΑΦΡΑΣΗ":"TRANSLATION", "Αγγλικό κείμενο":"English text", "Επιβεβαίωσε ότι το αποτέλεσμα διατηρεί το νόημά σου.":"Make sure the result preserves your meaning.", "Μετάφραση στα αγγλικά":"Translate to English", "Μετάφραση στα αγγλικά →":"Translate to English →", "Μετάφραση στα ελληνικά →":"Translate to Greek →", "Εγκρίνω τη μετάφραση":"Approve translation", "Αποθήκευση σε TXT":"Save as TXT", "Η μετάφραση χρειάζεται τον έλεγχό σου.":"Please review the translation.",
    "Εγκατάσταση ελληνικά → αγγλικά":"Install Greek → English", "Εγκατάσταση αγγλικά → ελληνικά":"Install English → Greek", "Έλεγχος διαθεσιμότητας":"Check availability", "Έλεγχος Argos…":"Checking Argos…", "Το επιλεγμένο γλωσσικό πακέτο είναι εγκατεστημένο.":"The selected language package is installed.", "Λείπει το επιλεγμένο γλωσσικό πακέτο.":"The selected language package is missing.", "Το Argos δεν είναι διαθέσιμο στο Python της εφαρμογής.":"Argos is unavailable in the application's Python environment.", "Δεν ήταν δυνατός ο έλεγχος του Argos.":"Could not check Argos availability.", "Το Argos μεταφράζει χωρίς μοντέλο Ollama.":"Argos translates without an Ollama model.",
    "Αλλαγή ύψους επιλογών Writer":"Resize Writer options", "Αλλαγή ύψους επιλογών μετάφρασης":"Resize translation options", "Απόκρυψη στήλης":"Hide column", "Εμφάνιση στήλης":"Show column", "Τα κείμενά σου δεν αποθηκεύονται αυτόματα. Αποθήκευσέ τα πριν κλείσεις.":"Your texts are not saved automatically. Save them before closing.", "Τοπική λειτουργία · Ollama / Argos":"Local operation · Ollama / Argos", "Κλείσιμο":"Close", "Writer & Translator · Τοπικό πρωτότυπο":"Writer & Translator · Local prototype", "Η εφαρμογή χρησιμοποιεί τοπικά μοντέλα. Έλεγχε τα παραγόμενα κείμενα.":"The application uses local models. Review generated text.",
    "Πρόσθεσε σημειώσεις, δημιούργησε και έλεγξε το ελληνικό κείμενο. Για αγγλικά προς ελληνικά επίλεξε την κατεύθυνση και πρόσθεσε αγγλικό κείμενο. Έγκρινε το πρωτότυπο πριν από τη μετάφραση και έλεγξε το αποτέλεσμα πριν την αποθήκευση.":"Add notes, generate and review the Greek text. For English to Greek, select that direction and add English text. Approve the source before translating and review the result before saving.", "Αποθήκευσε τα κείμενά σου πριν κλείσεις την εφαρμογή. Τα κείμενα δεν αποθηκεύονται αυτόματα.":"Save your texts before closing the application. Texts are not saved automatically.",
    "Εγκατεστημένα μοντέλα":"Installed models", "Τα τοπικά μοντέλα μπορεί να χρησιμοποιούνται και από άλλες εφαρμογές.":"Local models may also be used by other applications.", "Εύρεση και εγκατάσταση":"Find and install", "Βρες το ακριβές όνομα στην":"Find the exact name in the", "επίσημη βιβλιοθήκη Ollama":"official Ollama library", "και πληκτρολόγησέ το παρακάτω.":"and enter it below.", "Η βιβλιοθήκη και η λήψη χρειάζονται σύνδεση στο διαδίκτυο και διαθέσιμο χώρο. Δεν ελέγχεται αυτόματα αν υπάρχει το όνομα.":"The library and download require internet access and disk space. Names are not checked automatically.", "Όνομα μοντέλου":"Model name", "Εγκατάσταση":"Install", "Πρόοδος λήψης":"Download progress", "Δεν υπάρχει ενεργή λήψη.":"There is no active download.", "Δεν βρέθηκαν τοπικά εγκατεστημένα μοντέλα.":"No locally installed models found.", "Μέγεθος μη διαθέσιμο":"Size unavailable", "Διαγραφή":"Delete", "Η λίστα ενημερώθηκε.":"The list was refreshed.", "Το μοντέλο διαγράφηκε.":"The model was deleted.", "Πληκτρολόγησε το όνομα του μοντέλου.":"Enter a model name.", "Αναμονή για στοιχεία προόδου από το Ollama.":"Waiting for download progress from Ollama.",
    "Περιορισμένοι τοπικοί κανόνες: ενώνουν bullets με τελική στίξη, χωρίς γραμματικό έλεγχο ή συμπλήρωση. Οι ελλιπείς σημειώσεις παραμένουν. Έλεγξε και επεξεργάσου το κείμενο.":"Limited local rules join punctuated bullets without grammar checking or completion. Incomplete notes remain. Review and edit the text.",
    "Μερικό αποτέλεσμα: αμφίσημες ή μη ολοκληρωμένες σημειώσεις διατηρήθηκαν. Έλεγξέ τες πριν την έγκριση.":"Partial result: ambiguous or incomplete notes were preserved. Review them before approval.",
    "Το γλωσσικό πακέτο για την επιλεγμένη κατεύθυνση δεν είναι εγκατεστημένο. Το κείμενό σου παραμένει διαθέσιμο.":"The language package for the selected direction is not installed. Your text remains available.",
    "Το τοπικό Ollama δεν είναι διαθέσιμο ή επέστρεψε σφάλμα. Το κείμενό σου παραμένει διαθέσιμο.":"Local Ollama is unavailable or returned an error. Your text remains available.",
    "Το γλωσσικό πακέτο εγκαταστάθηκε.":"The language package was installed.", "Αναζήτηση του γλωσσικού πακέτου…":"Searching for the language package…", "Λήψη του γλωσσικού πακέτου…":"Downloading the language package…", "Εγκατάσταση του γλωσσικού πακέτου…":"Installing the language package…",
    "Stop εργασίας":"Stop task", "Η αίτηση διακόπηκε. Το αρχικό κείμενο παραμένει διαθέσιμο.":"The request was stopped. The original text remains available.", "Η αίτηση διακόπηκε. Το Ollama μπορεί να συνεχίζει προσωρινά τη δική του επεξεργασία.":"The request was stopped. Ollama may temporarily continue its own processing.",
    "Η εργασία απέτυχε.":"The task failed.",
    "Η αίτηση δεν επιτρέπεται.":"The request is not allowed.",
    "Μη έγκυρη διεύθυνση.":"Invalid address.",
    "Δεν βρέθηκε.":"Not found.",
    "Μη έγκυρη αίτηση.":"Invalid request.",
    "Ελέγξτε το κείμενο και το μοντέλο.":"Check the text and model.",
    "Μια εργασία βρίσκεται ήδη σε εξέλιξη.":"A task is already running.",
    "Δεν ήταν δυνατή η έναρξη της εργασίας.":"Could not start the task.",
    "Η εργασία διακόπηκε απρόσμενα.":"The task stopped unexpectedly.",
    "Απαιτείται επιβεβαίωση εγκατάστασης.":"Installation confirmation is required.",
    "Απαιτείται επιβεβαίωση διαγραφής.":"Deletion confirmation is required.",
    "Μη έγκυρη κατεύθυνση μετάφρασης.":"Invalid translation direction.",
    "Το γλωσσικό πακέτο για την επιλεγμένη κατεύθυνση δεν είναι εγκατεστημένο.":"The language package for the selected direction is not installed.",
    "Το Argos δεν είναι διαθέσιμο στο Python της εφαρμογής. Έλεγξε την εγκατάσταση και τις εξαρτήσεις του.":"Argos is unavailable in the application Python. Check its installation and dependencies.",
    "Πρόσθεσε έγκυρο ελληνικό κείμενο.":"Add valid text.",
    "Δεν βρέθηκε το επιλεγμένο γλωσσικό ζεύγος.":"The selected language pair was not found.",
    "Μη συμβατή έκδοση Argos για τοπική μετάφραση.":"The Argos version is incompatible with local translation.",
    "Η τοπική μετάφραση Argos απέτυχε. Έλεγξε το γλωσσικό πακέτο και τα τοπικά αρχεία του.":"Local Argos translation failed. Check the language package and its local files.",
    "Το γλωσσικό πακέτο είναι ήδη εγκατεστημένο.":"The language package is already installed.",
    "Δεν βρέθηκε το επιλεγμένο γλωσσικό πακέτο στον κατάλογο Argos.":"The selected language package was not found in the Argos catalogue.",
    "Η εγκατάσταση δεν επιβεβαιώθηκε. Έλεγξε το πακέτο Argos.":"Installation was not confirmed. Check the Argos package.",
    "Η λήψη ή η εγκατάσταση απέτυχε. Έλεγξε τη σύνδεση και τον διαθέσιμο χώρο.":"Download or installation failed. Check the connection and disk space.",
    "Η απάντηση του Ollama είναι πολύ μεγάλη.":"The Ollama response is too large.",
    "Το τοπικό Ollama δεν είναι διαθέσιμο ή επέστρεψε σφάλμα.":"Local Ollama is unavailable or returned an error.",
    "Δεν ήταν δυνατή η ανάγνωση των μοντέλων.":"Could not read the models.",
    "Το επιλεγμένο τοπικό μοντέλο δεν είναι διαθέσιμο.":"The selected local model is unavailable.",
    "Το μοντέλο δεν επιβεβαιώθηκε ως τοπικό.":"The model could not be confirmed as local.",
    "Μη έγκυρη εργασία.":"Invalid task.",
    "Το μοντέλο δεν επέστρεψε κείμενο.":"The model returned no text.",
    "Το μοντέλο επέστρεψε ελλιπές αποτέλεσμα. Το πρωτότυπο διατηρήθηκε.":"The model returned an incomplete result. The original was preserved.",
    "Μη έγκυρο όνομα. Χρησιμοποίησε όνομα τοπικού μοντέλου από το Ollama.":"Invalid name. Use a local model name from Ollama.",
    "Το μοντέλο είναι ήδη εγκατεστημένο.":"The model is already installed.",
    "Σύνδεση με το Ollama…":"Connecting to Ollama…",
    "Δεν ήταν δυνατή η έναρξη της λήψης.":"Could not start the download.",
    "Μη έγκυρη απάντηση προόδου από το Ollama.":"Invalid progress response from Ollama.",
    "Η λήψη απέτυχε. Έλεγξε το όνομα, τη σύνδεση και τον διαθέσιμο χώρο.":"Download failed. Check the name, connection and disk space.",
    "Το μοντέλο δεν βρέθηκε. Έλεγξε το ακριβές όνομα στη βιβλιοθήκη Ollama.":"The model was not found. Check its exact name in the Ollama library.",
    "Η λήψη σταμάτησε πριν επιβεβαιωθεί η ολοκλήρωση.":"The download stopped before completion was confirmed.",
    "Το Ollama ανέφερε επιτυχία, αλλά το μοντέλο δεν εμφανίστηκε στη λίστα.":"Ollama reported success, but the model was not listed.",
    "Το μοντέλο εγκαταστάθηκε.":"The model was installed.",
    "Η λήψη απέτυχε. Έλεγξε το Ollama, τη σύνδεση και τον διαθέσιμο χώρο.":"Download failed. Check Ollama, the connection and disk space.",
    "Η λήψη απέτυχε. Έλεγξε το όνομα, το Ollama, τη σύνδεση και τον διαθέσιμο χώρο.":"Download failed. Check the name, Ollama, the connection and disk space.",
    "Μη έγκυρο όνομα μοντέλου.":"Invalid model name.",
    "Το μοντέλο δεν βρέθηκε στα τοπικά εγκατεστημένα μοντέλα.":"The model was not found among locally installed models.",
    "Η διαγραφή απέτυχε.":"Deletion failed.",
    "Η διαγραφή απέτυχε. Έλεγξε το τοπικό Ollama.":"Deletion failed. Check local Ollama.",
    "Το κείμενό σου παραμένει διαθέσιμο.":"Your text remains available.",
    "Η ενέργεια απέτυχε.":"The operation failed.",
    "Εγκρίθηκε για μετάφραση.":"Approved for translation.", "Εγκρίθηκε για αποθήκευση.":"Approved for saving.", "Ολοκληρώθηκε. Έλεγξε το αποτέλεσμα.":"Completed. Review the result.", "Πρόσθεσε κείμενο και, για Ollama, επίλεξε μοντέλο.":"Add text and, for Ollama, select a model.", "Επίλεξε ένα εγκατεστημένο τοπικό μοντέλο.":"Select an installed local model.", "Δεν βρέθηκαν τοπικά μοντέλα Ollama.":"No local Ollama models found.", "Η τοπική εφαρμογή δεν είναι διαθέσιμη.":"The local application is unavailable.", "Το τοπικό μοντέλο εργάζεται. Περίμενε…":"The local model is working. Please wait…", "Το Argos μεταφράζει τοπικά. Περίμενε…":"Argos is translating locally. Please wait…", "Οι τοπικοί κανόνες επεξεργάζονται τις σημειώσεις…":"Local rules are processing the notes…", "Πρώτα ενέκρινε και μετάφρασε το τρέχον κείμενο.":"First approve and translate the current text.", "Το αρχείο ζητήθηκε από τον browser. Επιβεβαίωσε ότι αποθηκεύτηκε.":"The browser was asked to save the file. Confirm it was saved.", "Η εφαρμογή τερματίστηκε. Κλείσε αυτή την καρτέλα.":"The application has stopped. Close this tab.",
    "Υπάρχει ήδη κείμενο σε αυτό το πεδίο. Να αντικατασταθεί;":"This field already contains text. Replace it?", "Να τερματιστεί η εφαρμογή; Αποθήκευσε πρώτα όσα κείμενα θέλεις να κρατήσεις.":"Stop the application? First save the texts you want to keep.", "Να γίνει λήψη και εγκατάσταση του επιλεγμένου γλωσσικού πακέτου Argos; Χρειάζεται σύνδεση και χώρος. Το πακέτο μπορεί να χρησιμοποιείται και από άλλες εφαρμογές.":"Download and install the selected Argos language package? Internet and disk space are required. Other applications may also use this package.",
    "Γράψε τις σημειώσεις σου":"Write your notes", "Το ελληνικό προσχέδιο θα εμφανιστεί εδώ.":"The Greek draft will appear here.", "Η αγγλική μετάφραση θα εμφανιστεί εδώ.":"The English translation will appear here.", "Η ελληνική μετάφραση θα εμφανιστεί εδώ.":"The Greek translation will appear here.", "Γράψε ή επικόλλησε το αγγλικό κείμενο.":"Write or paste English text.", "Όνομα από τη βιβλιοθήκη Ollama":"Name from the Ollama library"
  };
  let lang = "el";
  window.uiIsEnglish = () => lang === "en";
  const textOriginal = new WeakMap(), attrOriginal = new WeakMap();
  const attributes = ["placeholder", "aria-label", "title"];
  function applyText(node) {
    if (!node.parentElement || ["SCRIPT", "STYLE", "TEXTAREA"].includes(node.parentElement.tagName)) return;
    const value = node.nodeValue, trimmed = value.trim();
    if (!trimmed) return;
    const previous = textOriginal.get(node);
    const original = previous && (trimmed === previous || trimmed === en[previous]) ? previous : trimmed;
    if (!en[original]) return;
    textOriginal.set(node, original);
    const changed = value.replace(trimmed, lang === "en" ? en[original] : original);
    if (changed !== value) node.nodeValue = changed;
  }
  function applyElement(node) {
    if (node.nodeType !== Node.ELEMENT_NODE) return;
    let originals = attrOriginal.get(node) || {};
    for (const attr of attributes) {
      const value = node.getAttribute(attr);
      if (!value) continue;
      const previous = originals[attr];
      const original = previous && (value === previous || value === en[previous] || (previous.startsWith("Διαγραφή μοντέλου ") && value === "Delete model " + previous.slice("Διαγραφή μοντέλου ".length))) ? previous : value;
      const deletion = original.startsWith("Διαγραφή μοντέλου ");
      if (!en[original] && !deletion) continue;
      originals[attr] = original;
      const changed = lang === "en" ? (deletion ? "Delete model " + original.slice("Διαγραφή μοντέλου ".length) : en[original]) : original;
      if (value !== changed) node.setAttribute(attr, changed);
    }
    attrOriginal.set(node, originals);
  }
  function applyTree(root) {
    if (root.nodeType === Node.TEXT_NODE) return applyText(root);
    if (root.nodeType !== Node.ELEMENT_NODE && root.nodeType !== Node.DOCUMENT_NODE) return;
    if (root.nodeType === Node.ELEMENT_NODE) applyElement(root);
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) walker.currentNode.nodeType === Node.TEXT_NODE ? applyText(walker.currentNode) : applyElement(walker.currentNode);
  }
  function setLanguage(value) {
    lang = value; document.documentElement.lang = value;
    try { localStorage.setItem("writer-language", value); } catch {}
    document.getElementById("lang-el").setAttribute("aria-pressed", String(value === "el"));
    document.getElementById("lang-en").setAttribute("aria-pressed", String(value === "en"));
    applyTree(document.body);
  }
  window.translateUi = value => lang === "en" && en[value] ? en[value] : value;
  document.getElementById("lang-el").addEventListener("click", () => setLanguage("el"));
  document.getElementById("lang-en").addEventListener("click", () => setLanguage("en"));
  let initialLanguage = "en";
  try { if (localStorage.getItem("writer-language") === "el") initialLanguage = "el"; } catch {}
  setLanguage(initialLanguage);
  new MutationObserver(records => records.forEach(record => {
    if (record.type === "characterData") applyText(record.target);
    else if (record.type === "attributes") applyElement(record.target);
    else record.addedNodes.forEach(applyTree);
  })).observe(document.body, {subtree:true, childList:true, characterData:true, attributes:true, attributeFilter:attributes});
})();
