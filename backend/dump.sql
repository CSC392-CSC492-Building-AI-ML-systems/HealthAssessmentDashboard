CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    province VARCHAR(100) NOT NULL,
    description TEXT,
    location VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT uq_organization_name_province UNIQUE (name, province)
);
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    password_hash TEXT NOT NULL,
    organization_id INTEGER REFERENCES organizations(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
INSERT INTO users VALUES('omarelmalak@gmail.com','Omar','El Malak','$2b$12$ybxrHboj32yGLj7r5M8PjeBizd0qYKV7mwRKEnZ0a8n5O8FO5AXzi',0,1,'2025-08-28 02:17:03.114535','2025-08-28 02:17:03.114539');
INSERT INTO users VALUES('omar@gmail.com','Omar','El Malak','$2b$12$bj9N72FxDUMbnzn6oh2uTu.X/Z/JRRm2wbc7y/.XbYxHE9DqRU85m',0,2,'2025-08-28 02:18:56.870026','2025-08-28 02:18:56.870029');
INSERT INTO users VALUES('test@gmail.com','Omar','El Malak','$2b$12$WAr8qQKknJv4SMglQHf65.otYXK.gtEzYiqed/noRKt5oNFYqY2WW',NULL,3,'2025-09-07 18:38:24.640035','2025-09-07 18:38:24.640042');
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id),
    therapeutic_areas JSONB NOT NULL,
    news_preferences TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
INSERT INTO user_preferences VALUES(3,'["Oncology", "Dermatology"]','arsdaf',1,'2025-09-07 18:38:24.667403','2025-09-07 18:38:24.667406');
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    chat_summary TEXT NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
INSERT INTO chat_history VALUES('New Chat 1',3,1,'2025-09-07 20:44:25.648121','2025-09-07 20:44:25.648137');
INSERT INTO chat_history VALUES('New Chat 1',3,2,'2025-09-07 20:48:13.387367','2025-09-07 20:48:13.387381');
INSERT INTO chat_history VALUES('New Chat 1',3,3,'2025-09-07 20:49:43.009163','2025-09-07 20:49:43.009186');
INSERT INTO chat_history VALUES('New Chat 1',3,4,'2025-09-07 20:51:35.293955','2025-09-07 20:51:35.293964');
INSERT INTO chat_history VALUES('New Cha',3,5,'2025-09-07 21:30:34.639786','2025-09-07 22:01:25.427914');
INSERT INTO chat_history VALUES('New Chat 6',3,6,'2025-09-07 21:30:48.842039','2025-09-07 21:30:48.842053');
INSERT INTO chat_history VALUES('New Chat 7',3,7,'2025-09-09 23:12:18.039293','2025-09-09 23:12:18.039304');
CREATE TABLE drugs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    generic_name VARCHAR(255),
    project_number VARCHAR(100),
    therapeutic_area VARCHAR(255),
    submission_date DATE,
    dosage_form VARCHAR(255),
    din VARCHAR(50),
    therapeutic_value VARCHAR(255),
    cost_effectiveness DOUBLE PRECISION,
    manufacturer_price DOUBLE PRECISION,
    reimbursement_restrictions TEXT,
    drug_type VARCHAR(100),
    submission_pathway VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
INSERT INTO drugs VALUES(1,'aaa',NULL,NULL,NULL,NULL,NULL,'2223',NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'2025-08-28 03:54:26.632535','2025-08-28 03:54:26.632543');
INSERT INTO drugs VALUES(1,'aaaa',NULL,NULL,NULL,NULL,NULL,'aaa',NULL,NULL,NULL,NULL,NULL,NULL,NULL,2,'2025-08-28 03:59:53.105125','2025-08-28 03:59:53.105133');
INSERT INTO drugs VALUES(1,'aaaa',NULL,NULL,NULL,NULL,NULL,'aaa',NULL,NULL,NULL,NULL,NULL,NULL,NULL,3,'2025-08-28 04:01:52.437639','2025-08-28 04:01:52.437643');
INSERT INTO drugs VALUES(1,'aaaa',NULL,NULL,NULL,NULL,NULL,'aaa',NULL,NULL,NULL,NULL,NULL,NULL,NULL,4,'2025-08-28 04:04:27.379388','2025-08-28 04:04:27.379393');
INSERT INTO drugs VALUES(1,'aaaa',NULL,NULL,NULL,NULL,NULL,'aaa',NULL,NULL,NULL,NULL,NULL,NULL,NULL,5,'2025-08-28 04:07:06.577340','2025-08-28 04:07:06.577351');
INSERT INTO drugs VALUES(1,'aaaa',NULL,NULL,NULL,NULL,NULL,'aaa',NULL,NULL,NULL,NULL,NULL,NULL,NULL,6,'2025-08-28 04:07:32.819395','2025-08-28 04:07:32.819400');
INSERT INTO drugs VALUES(2,'aaaa','sasd','sdad','asdasd',NULL,'asdadsad','adsasd','adsasd',12.0,12.0,'asdasd','standard','standard','asd',7,'2025-08-28 05:26:51.923293','2025-08-28 05:26:51.923301');
INSERT INTO drugs VALUES(2,'aaaa','sasd','sdad','asdasd',NULL,'asdadsad','adsasd','adsasd',12.0,12.0,'asdasd','standard','standard','asd',8,'2025-08-28 05:38:46.038856','2025-08-28 05:38:46.038860');
INSERT INTO drugs VALUES(2,'aaaa','sasd','sdad','asdasd',NULL,'asdadsad','adsasd','adsasd',12.0,12.0,'asdasd','standard','standard','asd',9,'2025-08-28 05:42:09.256219','2025-08-28 05:42:09.256230');
INSERT INTO drugs VALUES(2,'saA','ASa','as','s',NULL,'adad','sdfdsf','ASasaS',12.0,12.0,'asdsd','rare_disease','conditional',NULL,10,'2025-08-28 05:43:00.932534','2025-08-28 05:43:00.932540');
INSERT INTO drugs VALUES(2,'saA','ASa','as','s','2025-08-14','adad','sdfdsf','ASasaS',12.0,12.0,'asdsd','rare_disease','conditional','asdasd',11,'2025-08-28 05:43:57.153023','2025-08-28 05:43:57.153030');
INSERT INTO drugs VALUES(2,'saA','ASa','as','s','2025-08-14','adad','sdfdsf','ASasaS',12.0,12.0,'asdsd','rare_disease','conditional','asdasd',12,'2025-08-28 05:45:14.965972','2025-08-28 05:45:14.965980');
INSERT INTO drugs VALUES(2,'fsfjgjkfg','ASa','as','s','2025-08-14','adad','sdfdsf','ASasaS',12.0,12.0,'asdsd','rare_disease','conditional','asdasd',13,'2025-08-28 05:46:03.037168','2025-08-28 05:46:03.037174');
INSERT INTO drugs VALUES(2,'dfgdfgjdfg','ASa','as','s','2025-08-14','adad','sdfdsf','ASasaS',12.0,12.0,'asdsd','rare_disease','conditional','asdasd',14,'2025-08-28 05:47:08.747510','2025-08-28 05:47:08.747517');
INSERT INTO drugs VALUES(2,'dfgdfgjdfg','ASa','as','s','2025-08-14','adad','sdfdsf','ASasaS',12.0,12.0,'asdsd','rare_disease','conditional','asdasd',15,'2025-08-28 05:48:59.384672','2025-08-28 05:48:59.384681');
INSERT INTO drugs VALUES(2,'dgsgsfdg','ASa','as','s','2025-08-14','adad','sdfdsf','ASasaS',12.0,12.0,'asdsd','rare_disease','conditional','asdasd',16,'2025-08-28 05:50:09.103281','2025-08-28 05:50:09.103288');
INSERT INTO drugs VALUES(2,'gdfgdsfg','sdsdgg','adgf','dfg','2025-08-09','afgfg','dgsd','dfsgsdg',12.0,12.0,'sffdg','rare_disease','conditional',NULL,17,'2025-08-28 06:08:28.297211','2025-08-28 06:08:28.297216');
INSERT INTO drugs VALUES(2,'adas','asdads','asdsd','asdasd','2025-08-08','asdasd','asdsad','asd',23.0,43.0,'ad','biologic','standard','adsad',18,'2025-08-28 17:53:11.956026','2025-08-28 17:53:11.956031');
INSERT INTO drugs VALUES(2,'Test','test','test','test','2025-07-31','test','test','test',11.0,11.0,'test','oncology','priority','llkdjsflk',19,'2025-08-28 18:02:37.672340','2025-08-28 18:02:37.672349');
INSERT INTO drugs VALUES(2,'Test','test','test','test','2025-08-08','test','test','test',123.0,123.0,'test','oncology','priority','test',20,'2025-08-28 18:04:30.351081','2025-08-28 18:04:30.351090');
INSERT INTO drugs VALUES(2,'test','tst','test','test','2025-08-07','test','1234','test',12.0,14.0,'test','biologic','standard','test',21,'2025-08-28 18:11:42.503515','2025-08-28 18:11:42.503523');
CREATE TABLE chat_message (
    id SERIAL PRIMARY KEY,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    chat_history_id INTEGER NOT NULL REFERENCES chat_history(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
INSERT INTO chat_message VALUES('USER','sdfdsf',2,1,'2025-08-28 17:55:25.502625','2025-08-28 17:55:25.502635');
INSERT INTO chat_message VALUES('ASSISTANT',unistr('None.  \u000a\u000a- No relevant information was provided to address the query.  \u000a- The context snippets contain incomplete and unclear data.  \u000a\u000a- The query lacks specific details or context for a meaningful response.  \u000a- No predictions or calculations can be made based on the provided evidence.  \u000a\u000aSources:  \u000aNone.'),2,2,'2025-08-28 17:55:25.502635','2025-08-28 17:55:25.502635');
INSERT INTO chat_message VALUES('USER','Give me the indication for dupixent',2,3,'2025-08-28 18:04:48.482434','2025-08-28 18:04:48.482448');
INSERT INTO chat_message VALUES('ASSISTANT',unistr('Dupixent (dupilumab) is indicated for the treatment of patients aged 12 years and older with moderate-to-severe atopic dermatitis whose disease is not adequately controlled with topical prescription therapies or when those therapies are not advisable.\u000a\u000aKey details:\u000a- Indication: Moderate-to-severe atopic dermatitis\u000a- Age group: 12 years and older\u000a- Treatment context: Insufficient control with topical therapies\u000a\u000aCaveats/assumptions:\u000a- This information is based on available clinical review reports.\u000a- No predictions regarding pricing or timelines are provided.\u000a- This response does not constitute medical advice.\u000a\u000aSources:  \u000a/scratch/vaidik/etl/data/Preprocessing/Data/pdfs/SF0754-000_1.pdf  \u000a/scratch/vaidik/etl/data/Preprocessing/Data/pdfs/SR0774-000_2.pdf  \u000a/scratch/vaidik/etl/data/Preprocessing/Data/pdfs/SR0667-000_2.pdf'),2,4,'2025-08-28 18:04:48.482449','2025-08-28 18:04:48.482450');
INSERT INTO chat_message VALUES('USER','What are the key clinical trials supporting Dupixent approval?',2,5,'2025-08-28 18:05:58.505703','2025-08-28 18:05:58.505724');
INSERT INTO chat_message VALUES('ASSISTANT',unistr('Dupixent (dupilumab) approval in Canada is supported by several key clinical trials, including the phase III Liberty Asthma QUEST trial and multiple studies in atopic dermatitis (AD), such as Study 1526, which evaluated its efficacy and safety in adolescents. These trials demonstrated significant improvements in disease severity and quality of life compared to placebo.\u000a\u000aKey details:\u000a- Liberty Asthma QUEST: Phase III trial for uncontrolled moderate-to-severe asthma.\u000a- Study 1526: Phase III trial for adolescents with moderate-to-severe AD, focusing on IGA and EASI outcomes.\u000a- Other relevant studies include SOLO 1, SOLO 2, LIBERTY AD CHRONOS, and SOLO CONTINUE.\u000a\u000aCaveats/assumptions:\u000a- The information is based on available clinical trial data and may not encompass all studies.\u000a- The outcomes and efficacy may vary based on individual patient characteristics.\u000a- This response does not constitute medical advice.\u000a\u000aSources:  \u000a/scratch/vaidik/etl/data/Preprocessing/Data/pdfs/SR0667-000_2.pdf  \u000a/scratch/vaidik/etl/data/Preprocessing/Data/pdfs/SR0636-000_0.pdf  \u000a/scratch/vaidik/etl/data/Preprocessing/Data/pdfs/SR0636-000_0.pdf'),2,6,'2025-08-28 18:05:58.505726','2025-08-28 18:05:58.505727');
INSERT INTO chat_message VALUES('USER','What are the key clinical trial outcomes supporting Dupixent approval?',2,7,'2025-08-28 18:07:40.518587','2025-08-28 18:07:40.518603');
INSERT INTO chat_message VALUES('ASSISTANT',unistr('Dupixent (dupilumab) was supported for approval in Canada based on two phase III, double-blind randomized controlled trials (RCTs) demonstrating its efficacy in treating moderate-to-severe atopic dermatitis in patients aged 6 months and older. Key outcomes included significant improvements in the proportion of patients achieving an Investigator''s Global Assessment (IGA) score of 0 or 1, as well as reductions in the Eczema Area and Severity Index (EASI) score and daily worst itch scores.\u000a\u000aKey details:\u000a- Trials: LIBERTY AD PRESCHOOL (N = 162) and LIBERTY AD PEDS (N = 367).\u000a- Treatment duration: 16 weeks.\u000a- Primary endpoint: Proportion of patients with IGA score of 0 or 1 at week 16.\u000a- Key secondary endpoints: EASI-75, percent change from baseline in EASI score, and itch severity.\u000a\u000aCaveats/assumptions:\u000a- The data included a limited number of Canadian patients, raising questions about generalizability.\u000a- Treatment selection was at the discretion of physicians, potentially introducing bias.\u000a- The findings may not fully represent the broader pediatric population with atopic dermatitis in Canada.\u000a\u000aSources:\u000aNone.'),2,8,'2025-08-28 18:07:40.518605','2025-08-28 18:07:40.518606');
INSERT INTO chat_message VALUES('USER','What are the key clinical trial outcomes supporting Dupixent approval?',2,9,'2025-08-28 18:07:55.677396','2025-08-28 18:07:55.677421');
INSERT INTO chat_message VALUES('ASSISTANT',unistr('Dupixent (dupilumab) received approval based on two pivotal phase III randomized controlled trials (RCTs) demonstrating its efficacy in treating moderate-to-severe atopic dermatitis in patients aged 6 months and older. Key outcomes included significant improvements in the proportion of patients achieving an Investigator''s Global Assessment (IGA) score of 0 or 1 and notable reductions in eczema area and severity index (EASI) scores.\u000a\u000aKey details:\u000a- Trials: LIBERTY AD PRESCHOOL (N = 162) and LIBERTY AD PEDS (N = 367).\u000a- Treatment duration: 16 weeks.\u000a- Primary endpoint: Proportion of patients with IGA score of 0 or 1 at week 16.\u000a- Key secondary endpoints: EASI-75, percent change in EASI score, and improvement in itch severity.\u000a\u000aCaveats/assumptions:\u000a- Limited data on treatment selection and patient characteristics may affect the generalizability of results.\u000a- The interpretation of findings is complicated by the lack of control arms in some studies.\u000a- This response does not constitute medical advice.\u000a\u000aSources:  \u000a/scratch/vaidik/etl/data/Preprocessing/Data/pdfs/SR0774-000_2.pdf  \u000a/scratch/vaidik/etl/data/Preprocessing/Data/pdfs/SR0667-000_2.pdf  \u000a/scratch/vaidik/etl/data/Preprocessing/Data/pdfs/SR0636-000_0.pdf'),2,10,'2025-08-28 18:07:55.677423','2025-08-28 18:07:55.677424');
INSERT INTO chat_message VALUES('USER','Give me the indication for Dupixent',2,11,'2025-08-28 18:12:04.263003','2025-08-28 18:12:04.263015');
INSERT INTO chat_message VALUES('ASSISTANT',unistr('Dupixent (dupilumab) is indicated for the treatment of patients aged 12 years and older with moderate-to-severe atopic dermatitis that is not adequately controlled with topical prescription therapies or when those therapies are not advisable.\u000a\u000aKey details:\u000a- Approved for patients aged 12 and older.\u000a- Targets moderate-to-severe atopic dermatitis.\u000a- Used when topical therapies are ineffective or unsuitable.\u000a\u000aCaveats/assumptions:\u000a- This information is based on available clinical data and regulatory approvals.\u000a- No specific pricing information is provided for Dupixent in the context.\u000a\u000aSources:  \u000a/scratch/vaidik/etl/data/Preprocessing/Data/pdfs/SF0754-000_1.pdf  \u000a/scratch/vaidik/etl/data/Preprocessing/Data/pdfs/SR0667-000_2.pdf  \u000a/scratch/vaidik/etl/data/Preprocessing/Data/pdfs/SR0774-000_2.pdf'),2,12,'2025-08-28 18:12:04.263016','2025-08-28 18:12:04.263017');
INSERT INTO chat_message VALUES('USER','What are the key clinical trial outcomes supporting Dupixent approval?',2,13,'2025-08-28 18:13:07.609327','2025-08-28 18:13:07.609347');
INSERT INTO chat_message VALUES('ASSISTANT',unistr('Dupixent (dupilumab) was supported for approval in Canada based on two phase III, double-blind randomized controlled trials (RCTs) that demonstrated its efficacy in treating moderate-to-severe atopic dermatitis in patients aged 6 months and older. Key outcomes included significant improvements in the proportion of patients achieving an Investigator''s Global Assessment (IGA) score of 0 or 1 at week 16, as well as notable reductions in the Eczema Area and Severity Index (EASI) scores and daily itch severity.\u000a\u000aKey details:\u000a- Trials: LIBERTY AD PRESCHOOL (N = 162) and LIBERTY AD PEDS (N = 367).\u000a- Treatment duration: 16 weeks.\u000a- Primary endpoint: Proportion of patients with IGA score of 0 or 1 at week 16.\u000a- Key secondary endpoints: EASI-75, percent change in EASI score, and daily worst itch NRS score.\u000a\u000aCaveats/assumptions:\u000a- The data included a limited number of Canadian patients, raising questions about generalizability.\u000a- Treatment selection was not randomized, which may introduce bias.\u000a- The interpretation of findings is constrained by limited reporting on treatment comparators.\u000a\u000aSources:  \u000a/scratch/vaidik/etl/data/Preprocessing/Data/pdfs/SR0774-000_2.pdf  \u000a/scratch/vaidik/etl/data/Preprocessing/Data/pdfs/SR0667-000_2.pdf  \u000a/scratch/vaidik/etl/data/Preprocessing/Data/pdfs/SR0636-000_0.pdf'),2,14,'2025-08-28 18:13:07.609348','2025-08-28 18:13:07.609349');
INSERT INTO chat_message VALUES('USER','What is the indication for dupixent',1,15,'2025-09-07 18:39:03.951066','2025-09-07 18:39:03.951077');
INSERT INTO chat_message VALUES('ASSISTANT','Sorry, I’m unable to generate a response right now. Please try again in a moment.',1,16,'2025-09-07 18:39:03.951078','2025-09-07 18:39:03.951079');
INSERT INTO chat_message VALUES('USER','What is the indication for dupixent?]',1,17,'2025-09-07 18:39:12.697884','2025-09-07 18:39:12.697888');
INSERT INTO chat_message VALUES('ASSISTANT','Sorry, I’m unable to generate a response right now. Please try again in a moment.',1,18,'2025-09-07 18:39:12.697889','2025-09-07 18:39:12.697889');
INSERT INTO chat_message VALUES('USER','What is the indication for dupixent?',1,19,'2025-09-07 18:39:43.767148','2025-09-07 18:39:43.767153');
INSERT INTO chat_message VALUES('ASSISTANT','Sorry, I’m unable to generate a response right now. Please try again in a moment.',1,20,'2025-09-07 18:39:43.767153','2025-09-07 18:39:43.767154');
INSERT INTO chat_message VALUES('USER','Test',7,21,'2025-09-09 23:14:06.987589','2025-09-09 23:14:06.987599');
INSERT INTO chat_message VALUES('ASSISTANT','Sorry, I’m unable to generate a response right now. Please try again in a moment.',7,22,'2025-09-09 23:14:06.987601','2025-09-09 23:14:06.987601');
INSERT INTO chat_message VALUES('USER','test',7,23,'2025-09-09 23:14:07.604045','2025-09-09 23:14:07.604048');
INSERT INTO chat_message VALUES('ASSISTANT','Sorry, I’m unable to generate a response right now. Please try again in a moment.',7,24,'2025-09-09 23:14:07.604048','2025-09-09 23:14:07.604049');
CREATE TABLE drug_files (
    id SERIAL PRIMARY KEY,
    drug_id INTEGER NOT NULL REFERENCES drugs(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_size INTEGER,
    content_type VARCHAR(100),
    blob_url VARCHAR(500),
    vector_ids JSONB,
    chunk_count INTEGER,
    file_type VARCHAR(50),
    processing_status VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
INSERT INTO drug_files VALUES(1,8,2,'2_8_7b108838-afd1-4686-9899-d30af7f19ff9.pdf','SampleDrug_info.pdf',21733,'application/pdf','https://ourpathsvectordb.blob.core.windows.net/ourpathsdata/2_8_7b108838-afd1-4686-9899-d30af7f19ff9.pdf','["a852de9e-d02f-499c-98c7-8308fa954d75"]',1,'pdf','completed','2025-08-28 05:38:46');
INSERT INTO drug_files VALUES(2,9,2,'2_9_17a5598c-ff9c-41ff-8e9c-28ecd19ac861.pdf','SampleDrug_info.pdf',21733,'application/pdf','https://ourpathsvectordb.blob.core.windows.net/ourpathsdata/2_9_17a5598c-ff9c-41ff-8e9c-28ecd19ac861.pdf','["729b3747-bc82-4f12-af1c-6152ab2fca0e"]',1,'pdf','completed','2025-08-28 05:42:09');
INSERT INTO drug_files VALUES(3,12,2,'2_12_dfe2f6ce-ec0c-4a97-9046-52c5ff04c144.pdf','SampleDrug_info.pdf',21733,'application/pdf','https://ourpathsvectordb.blob.core.windows.net/ourpathsdata/2_12_dfe2f6ce-ec0c-4a97-9046-52c5ff04c144.pdf','["293fd801-4b92-4b05-9fb8-0d1a933f8397"]',1,'pdf','completed','2025-08-28 05:45:14');
INSERT INTO drug_files VALUES(4,13,2,'2_13_ae5cf89c-c698-46bc-9e19-9d04f88bb581.pdf','SampleDrug_info.pdf',21733,'application/pdf','https://ourpathsvectordb.blob.core.windows.net/ourpathsdata/2_13_ae5cf89c-c698-46bc-9e19-9d04f88bb581.pdf','["d3563874-a3bc-4d1a-bb8d-76c423a6bd0c"]',1,'pdf','completed','2025-08-28 05:46:03');
INSERT INTO drug_files VALUES(5,14,2,'2_14_5b84e708-c467-465d-abec-09c54e7edd9a.pdf','SampleDrug_info.pdf',21733,'application/pdf','https://ourpathsvectordb.blob.core.windows.net/ourpathsdata/2_14_5b84e708-c467-465d-abec-09c54e7edd9a.pdf','["2f5511e4-1037-49e9-8cec-31ded9df5e6a"]',1,'pdf','completed','2025-08-28 05:47:08');
INSERT INTO drug_files VALUES(6,15,2,'2_15_43552f9b-29a3-41f8-82f1-236b2db48e69.pdf','SampleDrug_info.pdf',21733,'application/pdf','https://ourpathsvectordb.blob.core.windows.net/ourpathsdata/2_15_43552f9b-29a3-41f8-82f1-236b2db48e69.pdf','["8b0b112c-a714-4cb5-9beb-d9a02376e464"]',1,'pdf','completed','2025-08-28 05:48:59');
INSERT INTO drug_files VALUES(7,16,2,'2_16_cd158be1-f111-4ac6-8fb3-48db0e6c2d20.pdf','SampleDrug_info.pdf',21733,'application/pdf','https://ourpathsvectordb.blob.core.windows.net/ourpathsdata/2_16_cd158be1-f111-4ac6-8fb3-48db0e6c2d20.pdf','["8ded8500-92d1-48cc-98c5-21d527be7142"]',1,'pdf','completed','2025-08-28 05:50:09');
INSERT INTO drug_files VALUES(8,17,2,'2_17_78194845-07c5-4508-9480-64b5b0a1f616.pdf','SR0878-Dupixent_NP_FINAL_Rec.pdf',659656,'application/pdf','https://ourpathsvectordb.blob.core.windows.net/ourpathsdata/2_17_78194845-07c5-4508-9480-64b5b0a1f616.pdf','["66d54deb-ceca-42f3-be93-1fcf23acb0ac", "680410ea-31f3-4592-97f0-eae63388c35e", "03eff7ef-12e5-4ffd-9483-43396c573f01", "d2ef53e6-636e-4e33-8fbf-ad2f021df95f", "3f72c517-3362-478b-b93e-c4758f43e443", "96523549-3628-4d2c-aeb8-a444e090816e", "7dd47908-ff65-4c45-a917-fb9879e489ab", "1a3b3fa7-4ba4-4660-802f-757241d64460", "ff0ab272-5f4a-4006-8e37-2fa366d5ee2b", "fc4c6109-bb6b-465e-b015-21574c3c6742", "a0bc9bc8-f9e0-4ca6-b697-2f1a7dd8c603", "65aff0d4-7fac-455e-96ed-fded57394c64", "54833a23-ea51-4074-8d6c-f93c08ad7b44", "6d1de20a-37af-4e51-90ba-7bed7d205852", "5927c104-af41-4882-a67e-17f86954d7b2", "da04fd70-897f-4742-b2ea-1641eaea2953", "be189271-ffce-4f65-ab3f-7d33ed6c992a"]',17,'pdf','completed','2025-08-28 06:08:28');
INSERT INTO drug_files VALUES(9,18,2,'2_18_88b96b3e-2e88-42dc-ba23-3c59fabed4f3.pdf','SampleDrug_info.pdf',21733,'application/pdf','https://ourpathsvectordb.blob.core.windows.net/ourpathsdata/2_18_88b96b3e-2e88-42dc-ba23-3c59fabed4f3.pdf','["301ef794-e20d-489c-8f49-57043caea46e"]',1,'pdf','completed','2025-08-28 17:53:11');
INSERT INTO drug_files VALUES(10,19,2,'2_19_8b7d5bab-f5d7-4053-8642-4279471f563b.pdf','Omar El Malak Resume 2025.pdf',115927,'application/pdf','https://ourpathsvectordb.blob.core.windows.net/ourpathsdata/2_19_8b7d5bab-f5d7-4053-8642-4279471f563b.pdf','["689ea8b1-6bb6-4d4a-ba25-1653285afecb"]',1,'pdf','completed','2025-08-28 18:02:37');
INSERT INTO drug_files VALUES(11,20,2,'2_20_7dc5ae5b-5bb3-494d-9246-0560b4462ae3.pdf','Omar El Malak Resume 2025.pdf',115927,'application/pdf','https://ourpathsvectordb.blob.core.windows.net/ourpathsdata/2_20_7dc5ae5b-5bb3-494d-9246-0560b4462ae3.pdf','["91f9af8a-6e80-40b5-b58e-483f3dc4ee8b"]',1,'pdf','completed','2025-08-28 18:04:30');
INSERT INTO drug_files VALUES(12,21,2,'2_21_dd837b9a-df08-4bc4-9805-42219cff6cff.pdf','Omar El Malak Resume 2025.pdf',115927,'application/pdf','https://ourpathsvectordb.blob.core.windows.net/ourpathsdata/2_21_dd837b9a-df08-4bc4-9805-42219cff6cff.pdf','["eb20e97e-0973-46e3-bac1-5d7b4f19d6b6"]',1,'pdf','completed','2025-08-28 18:11:42');
CREATE TABLE organization_drug_association (
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    drug_id INTEGER NOT NULL REFERENCES drugs(id) ON DELETE CASCADE,
    PRIMARY KEY (organization_id, drug_id)
);
CREATE INDEX ix_organizations_name ON organizations (name);
CREATE INDEX ix_users_organization_id ON users (organization_id);
CREATE UNIQUE INDEX ix_users_email ON users (email);
CREATE INDEX ix_drug_files_id ON drug_files (id);