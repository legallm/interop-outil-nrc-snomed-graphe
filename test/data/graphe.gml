graph [
  directed 1
  node [
    id 0
    label "129574000"
    fsn "Postoperative myocardial infarction (disorder)"
    pt_en "Postoperative myocardial infarction"
    pt_lang "infarctus myocardique postoperatoire"
  ]
  node [
    id 1
    label "1163440003"
    fsn "Postoperative acute myocardial infarction (disorder)"
    pt_en "Postoperative acute myocardial infarction"
    pt_lang "infarctus du myocarde aigu postoperatoire"
    syn_en "Acute myocardial infarction following operative procedure"
    syn_lang "IDM (infarctus du myocarde) aigu postoperatoire"
  ]
  node [
    id 2
    label "311796008"
    fsn "Postoperative subendocardial myocardial infarction (disorder)"
    pt_en "Postoperative subendocardial myocardial infarction"
    pt_lang "infarctus myocardique sous-endocardique postoperatoire"
  ]
  node [
    id 3
    label "311792005"
    fsn "Postoperative transmural myocardial infarction of anterior wall (disorder)"
    pt_en "Postoperative transmural myocardial infarction of anterior wall"
    pt_lang "infarctus myocardique transmural anterieur postoperatoire"
  ]
  node [
    id 4
    label "311793000"
    fsn "Postoperative transmural myocardial infarction of inferior wall (disorder)"
    pt_en "Postoperative transmural myocardial infarction of inferior wall"
    pt_lang "infarctus myocardique transmural inferieur postoperatoire"
  ]
  node [
    id 5
    label "116680003"
    fsn "Is a (attribute)"
    pt_en "Is a"
    pt_lang "est un(e)"
  ]
  node [
    id 6
    label "363698007"
    fsn "Finding site (attribute)"
    pt_en "Finding site"
    pt_lang "localisation de constatation"
  ]
  node [
    id 7
    label "116676008"
    fsn "Associated morphology (attribute)"
    pt_en "Associated morphology"
    pt_lang "morphologie associee"
    syn_en "Morphology"
  ]
  node [
    id 8
    label "255234002"
    fsn "After (attribute)"
    pt_en "After"
    syn_en "Following"
  ]
  node [
    id 9
    label "263502005"
    fsn "Clinical course (attribute)"
    pt_en "Clinical course"
    pt_lang "evolution clinique"
  ]
  node [
    id 10
    label "74281007"
    fsn "Myocardium structure (body structure)"
    pt_en "Myocardium structure"
    pt_lang "myocarde"
    syn_en "Cardiac muscle"
    syn_en "Myocardium"
    syn_lang "myocardium"
    syn_lang "structure du myocarde"
    syn_lang "structure myocardique"
  ]
  node [
    id 11
    label "55641003"
    fsn "Infarct (morphologic abnormality)"
    pt_en "Infarct"
    pt_lang "infarctus"
    syn_en "Infarction"
  ]
  node [
    id 12
    label "387713003"
    fsn "Surgical procedure (procedure)"
    pt_en "Surgical procedure"
    pt_lang "intervention chirurgicale"
    syn_en "Operation"
    syn_en "Operative procedure"
    syn_en "Surgery"
  ]
  node [
    id 13
    label "55470003"
    fsn "Acute infarct (morphologic abnormality)"
    pt_en "Acute infarct"
    syn_en "Recent infarct"
  ]
  node [
    id 14
    label "424124008"
    fsn "Sudden onset AND/OR short duration (qualifier value)"
    pt_en "Sudden onset AND/OR short duration"
    pt_lang "apparition soudaine ou de courte duree"
  ]
  node [
    id 15
    label "58148009"
    fsn "Structure of subendocardial myocardium (body structure)"
    pt_en "Structure of subendocardial myocardium"
    pt_lang "myocarde sous-endocardique"
    syn_en "Subendocardial myocardium"
  ]
  node [
    id 16
    label "6975006"
    fsn "Structure of anterior myocardium (body structure)"
    pt_en "Structure of anterior myocardium"
    pt_lang "myocarde anterieur"
    syn_en "Anterior myocardium"
    syn_lang "paroi anterieure du myocarde"
    syn_lang "structure du myocarde anterieur"
  ]
  node [
    id 17
    label "404684003"
    fsn "Clinical finding (finding)"
    pt_en "Clinical finding"
    pt_lang "constatation clinique"
  ]
  node [
    id 18
    label "900000000000441003"
    fsn "SNOMED CT Model Component (metadata)"
    pt_en "SNOMED CT Model Component"
  ]
  node [
    id 19
    label "123037004"
    fsn "Body structure (body structure)"
    pt_en "Body structure"
    pt_lang "structure corporelle"
    syn_en "Body structures"
  ]
  node [
    id 20
    label "71388002"
    fsn "Procedure (procedure)"
    pt_en "Procedure"
    pt_lang "procedure"
    syn_lang "intervention"
  ]
  node [
    id 21
    label "362981000"
    fsn "Qualifier value (qualifier value)"
    pt_en "Qualifier value"
    pt_lang "valeur de l'attribut"
  ]
  node [
    id 22
    label "138875005"
    fsn "SNOMED CT Concept (SNOMED RT+CTV3)"
    pt_en "SNOMED CT concept"
    pt_lang "concept SNOMED CT"
  ]
  node [
    id 23
    label "test"
    fsn "Test (test)"
    pt_en "Test" 
  ]
  edge [
    source 1
    target 0
    src "1163440003"
    tgt "129574000"
    group "0"
    attribute "116680003"
  ]
  edge [
    source 2
    target 0
    src "311796008"
    tgt "129574000"
    group "0"
    attribute "116680003"
  ]
  edge [
    source 3
    target 0
    src "311792005"
    tgt "129574000"
    group "0"
    attribute "116680003"
  ]
  edge [
    source 4
    target 0
    src "311793000"
    tgt "129574000"
    group "0"
    attribute "116680003"
  ]
  edge [
    source 5
    target 18
    src "116680003"
    tgt "900000000000441003"
    group "0"
    attribute "116680003"
  ]
  edge [
    source 6
    target 18
    src "363698007"
    tgt "900000000000441003"
    group "0"
    attribute "116680003"
  ]
  edge [
    source 7
    target 18
    src "116676008"
    tgt "900000000000441003"
    group "0"
    attribute "116680003"
  ]
  edge [
    source 8
    target 18
    src "255234002"
    tgt "900000000000441003"
    group "0"
    attribute "116680003"
  ]
  edge [
    source 9
    target 18
    src "263502005"
    tgt "900000000000441003"
    group "0"
    attribute "116680003"
  ]
  edge [
    source 10
    target 19
    src "74281007"
    tgt "123037004"
    group "0"
    attribute "116680003"
  ]
  edge [
    source 11
    target 19
    src "55641003"
    tgt "123037004"
    group "0"
    attribute "116680003"
  ]
  edge [
    source 13
    target 19
    src "55470003"
    tgt "123037004"
    group "0"
    attribute "116680003"
  ]
  edge [
    source 15
    target 19
    src "58148009"
    tgt "123037004"
    group "0"
    attribute "116680003"
  ]
  edge [
    source 16
    target 19
    src "6975006"
    tgt "123037004"
    group "0"
    attribute "116680003"
  ]
  edge [
    source 12
    target 20
    src "387713003"
    tgt "71388002"
    group "0"
    attribute "116680003"
  ]
  edge [
    source 14
    target 21
    src "424124008"
    tgt "362981000"
    group "0"
    attribute "116680003"
  ]
  edge [
    source 0
    target 17
    src "129574000"
    tgt "404684003"
    group "0"
    attribute "116680003"
  ]
  edge [
    source 17
    target 22
    src "404684003"
    tgt "138875005"
    group "0"
    attribute "116680003"
  ]
  edge [
    source 18
    target 22
    src "900000000000441003"
    tgt "138875005"
    group "0"
    attribute "116680003"
  ]
  edge [
    source 19
    target 22
    src "123037004"
    tgt "138875005"
    group "0"
    attribute "116680003"
  ]
  edge [
    source 20
    target 22
    src "71388002"
    tgt "138875005"
    group "0"
    attribute "116680003"
  ]
  edge [
    source 21
    target 22
    src "362981000"
    tgt "138875005"
    group "0"
    attribute "116680003"
  ]
  edge [
    source 23
    target 4
    src "test"
    tgt "311793000"
    group "0"
    attribute "116680003"
  ]
  edge [
    source 23
    target 5
    src "test"
    tgt "116680003"
    group "0"
    attribute "116680003"
  ]
  edge [
    source 0
    target 10
    src "129574000"
    tgt "74281007"
    group "1"
    attribute "363698007"
  ]
  edge [
    source 1
    target 10
    src "1163440003"
    tgt "74281007"
    group "1"
    attribute "363698007"
  ]
  edge [
    source 2
    target 15
    src "311796008"
    tgt "58148009"
    group "1"
    attribute "363698007"
  ]
  edge [
    source 3
    target 16
    src "311792005"
    tgt "6975006"
    group "1"
    attribute "363698007"
  ]
  edge [
    source 4
    target 10
    src "311793000"
    tgt "74281007"
    group "1"
    attribute "363698007"
  ]
  edge [
    source 0
    target 11
    src "129574000"
    tgt "55641003"
    group "1"
    attribute "116676008"
  ]
  edge [
    source 1
    target 13
    src "1163440003"
    tgt "55470003"
    group "1"
    attribute "116676008"
  ]
  edge [
    source 2
    target 11
    src "311796008"
    tgt "55641003"
    group "1"
    attribute "116676008"
  ]
  edge [
    source 3
    target 11
    src "311792005"
    tgt "55641003"
    group "1"
    attribute "116676008"
  ]
  edge [
    source 4
    target 11
    src "311793000"
    tgt "55641003"
    group "1"
    attribute "116676008"
  ]
  edge [
    source 0
    target 12
    src "129574000"
    tgt "387713003"
    group "2"
    attribute "255234002"
  ]
  edge [
    source 1
    target 12
    src "1163440003"
    tgt "387713003"
    group "2"
    attribute "255234002"
  ]
  edge [
    source 2
    target 12
    src "311796008"
    tgt "387713003"
    group "2"
    attribute "255234002"
  ]
  edge [
    source 3
    target 12
    src "311792005"
    tgt "387713003"
    group "2"
    attribute "255234002"
  ]
  edge [
    source 4
    target 12
    src "311793000"
    tgt "387713003"
    group "2"
    attribute "255234002"
  ]
  edge [
    source 1
    target 14
    src "1163440003"
    tgt "424124008"
    group "3"
    attribute "263502005"
  ]
]
