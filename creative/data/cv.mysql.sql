-- Michael Borck CV — MySQL import file
CREATE DATABASE IF NOT EXISTS `cv` CHARACTER SET utf8mb4;
USE `cv`;

-- Schema for the CV database (MySQL 8+)
SET FOREIGN_KEY_CHECKS=0;
DROP TABLE IF EXISTS `personal`;
DROP TABLE IF EXISTS `summary`;
DROP TABLE IF EXISTS `experience`;
DROP TABLE IF EXISTS `education`;
DROP TABLE IF EXISTS `skill`;
DROP TABLE IF EXISTS `project`;
DROP TABLE IF EXISTS `achievement`;
DROP TABLE IF EXISTS `publication`;
DROP TABLE IF EXISTS `grant`;
DROP TABLE IF EXISTS `certification`;
DROP TABLE IF EXISTS `service`;
DROP TABLE IF EXISTS `membership`;
DROP TABLE IF EXISTS `interest`;
DROP TABLE IF EXISTS `teaching_satisfaction`;
DROP TABLE IF EXISTS `teaching_innovation`;
CREATE TABLE `personal` (
  `id` INT NOT NULL,
  `name` VARCHAR(255),
  `email` VARCHAR(255),
  `phone` VARCHAR(255),
  `linkedin` VARCHAR(255),
  `github` VARCHAR(255),
  `portfolio` VARCHAR(255),
  `location` VARCHAR(255),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE `summary` (
  `id` INT NOT NULL,
  `summary_text` TEXT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE `experience` (
  `id` INT NOT NULL,
  `sort` INT NOT NULL DEFAULT 0,
  `title` VARCHAR(255),
  `organization` VARCHAR(255),
  `location` VARCHAR(255),
  `period` VARCHAR(255),
  `responsibilities` TEXT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE `education` (
  `id` INT NOT NULL,
  `sort` INT NOT NULL DEFAULT 0,
  `degree` VARCHAR(255),
  `field` VARCHAR(255),
  `institution` VARCHAR(255),
  `year` VARCHAR(255),
  `thesis` TEXT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE `skill` (
  `id` INT NOT NULL,
  `sort` INT NOT NULL DEFAULT 0,
  `category` VARCHAR(255),
  `subcategory` VARCHAR(255),
  `names` VARCHAR(255),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE `project` (
  `id` INT NOT NULL,
  `sort` INT NOT NULL DEFAULT 0,
  `name` VARCHAR(255),
  `description` TEXT,
  `year` VARCHAR(255),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE `achievement` (
  `id` INT NOT NULL,
  `sort` INT NOT NULL DEFAULT 0,
  `achievement_text` TEXT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE `publication` (
  `id` INT NOT NULL,
  `sort` INT NOT NULL DEFAULT 0,
  `kind` VARCHAR(255),
  `title` VARCHAR(255),
  `authors` VARCHAR(255),
  `year` VARCHAR(255),
  `venue` VARCHAR(255),
  `description` TEXT,
  `license` VARCHAR(255),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE `grant` (
  `id` INT NOT NULL,
  `sort` INT NOT NULL DEFAULT 0,
  `title` VARCHAR(255),
  `scheme` VARCHAR(255),
  `funder` VARCHAR(255),
  `role` VARCHAR(255),
  `amount` VARCHAR(255),
  `year` VARCHAR(255),
  `summary` VARCHAR(255),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE `certification` (
  `id` INT NOT NULL,
  `sort` INT NOT NULL DEFAULT 0,
  `name` VARCHAR(255),
  `year` VARCHAR(255),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE `service` (
  `id` INT NOT NULL,
  `sort` INT NOT NULL DEFAULT 0,
  `category` VARCHAR(255),
  `role` VARCHAR(255),
  `organization` VARCHAR(255),
  `project` VARCHAR(255),
  `year` VARCHAR(255),
  `period` VARCHAR(255),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE `membership` (
  `id` INT NOT NULL,
  `sort` INT NOT NULL DEFAULT 0,
  `organization` VARCHAR(255),
  `status` VARCHAR(255),
  `year` VARCHAR(255),
  `note` VARCHAR(255),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE `interest` (
  `id` INT NOT NULL,
  `sort` INT NOT NULL DEFAULT 0,
  `name` VARCHAR(255),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE `teaching_satisfaction` (
  `id` INT NOT NULL,
  `sort` INT NOT NULL DEFAULT 0,
  `metric` VARCHAR(255),
  `details` VARCHAR(255),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE `teaching_innovation` (
  `id` INT NOT NULL,
  `sort` INT NOT NULL DEFAULT 0,
  `name` VARCHAR(255),
  `description` TEXT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
SET FOREIGN_KEY_CHECKS=1;

-- personal
INSERT INTO `personal` (`id`, `name`, `email`, `phone`, `linkedin`, `github`, `portfolio`, `location`) VALUES (1, 'Michael Borck', 'michael.borck@curtin.edu.au', '0402 297 573', 'https://linkedin.com/in/michaelborck', 'https://github.com/michael-borck', 'https://borck.dev', 'Perth, WA');

-- summary
INSERT INTO `summary` (`id`, `summary_text`) VALUES (1, 'AI Leader and Cyber Security expert with 35+ years spanning military → academia → industry consulting. Author of the "Learning with AI" open-textbook series (Conversation, Not Delegation; The Human Edge; Speak Software; Model Data, Verify AI, plus domain companions), creator of innovative educational AI tools, and a leader in AI-enhanced pedagogy serving academics, education, agriculture and mining sectors. Founder of LocoLabo, a self-funded applied-AI research lab (12 projects, 52 GPUs, $0 sponsorship) mapping what small local models can do on hardware people already own, with a rare combination of technical depth and educational innovation expertise. Teaching philosophy grounded in three conceptual pillars - Caring, Competence, and Passion, with a core principle of "Make Contact Count."');

-- experience
INSERT INTO `experience` (`id`, `sort`, `title`, `organization`, `location`, `period`, `responsibilities`) VALUES (1, 1, 'Lecturer — School of Marketing and Management', 'Curtin University', 'Perth, WA', 'Feb 2016 – Present', 'AI Program Leadership - AI Leader for the School, developing new AI programs within undergraduate and postgraduate curricula
Research Leadership - Founder of LocoLabo, a self-funded applied-AI research lab (12 projects, 52 GPUs, $0 sponsorship) mapping what small local models can do on hardware people already own; umbrella for the Spanish-named project family (LocoLLM, LocoBanco, LocoEnsayo, LocoPuente, LocoAgente, LocoConvoy)
Core Teaching Areas - AI, Programming (Python), and Cyber Security
Curriculum Development - Backbone developer for Python and Web development programs
Cyber Security - Lead lecturer for cyber security programs with advanced digital forensics curriculum
Educational Innovation - Pioneer in AI-enhanced pedagogy and interactive learning methodologies, with teaching philosophy grounded in Caring, Competence, and Passion
Student Engagement - Achieved an 85.0% average student rating across 38 unit deliveries since 2019 (16 at 100%) through innovative assessment design including "Cloud Core" virtual company simulation
Executive Education - Providing AI training to academics, education professionals, agriculture and mining industry executives');
INSERT INTO `experience` (`id`, `sort`, `title`, `organization`, `location`, `period`, `responsibilities`) VALUES (2, 2, 'Course Lead — Information Systems', 'Curtin University', 'Perth, WA', '2020 – 2023', 'Course Lead for Information Systems undergraduate and postgraduate degree programs
Led the repositioning of the Master of Information Systems and Technology into a standalone degree
Unit coordination across multiple levels - postgraduate, undergraduate, core, non-core, and service units (domestic and international)
Advanced Canvas LMS and Blackboard development and customization
Creator of interactive educational tools and assessment frameworks');
INSERT INTO `experience` (`id`, `sort`, `title`, `organization`, `location`, `period`, `responsibilities`) VALUES (3, 3, 'Associate Lecturer', 'Curtin University', 'Perth, WA', 'Jan 2001 – Dec 2007', 'Academic Leadership - Provided departmental representation on institutional committees
Program Development - Developed and delivered comprehensive course material for Software Engineering and Computer Science degrees
International Coordination - Managed unit coordination across domestic and international campuses');
INSERT INTO `experience` (`id`, `sort`, `title`, `organization`, `location`, `period`, `responsibilities`) VALUES (4, 4, 'AI, IS & Educational Technology Consultant', 'Self-Employed', 'Perth, WA', 'Jan 2016 – Present', 'AI strategy and implementation consultation
IS/IT consultation and analysis
Educational technology consulting and training
Executive education training in AI for academics, education professionals, agriculture and mining industries');
INSERT INTO `experience` (`id`, `sort`, `title`, `organization`, `location`, `period`, `responsibilities`) VALUES (5, 5, 'Researcher', 'Curtin University', 'Perth, WA', 'Mar 2018 – 2019', 'Advanced AI Research - Investigation and development of CNN models and their application to the maritime environment
Applied Machine Learning - Focused research on computer vision applications for marine and coastal monitoring');
INSERT INTO `experience` (`id`, `sort`, `title`, `organization`, `location`, `period`, `responsibilities`) VALUES (6, 6, 'Software Contractor', 'CRCSI & Landgate WA', 'Perth, WA', 'Mar 2015 – Jan 2016', 'Computer Vision Innovation - Developed automated detection and recognition systems for street sign inventory
Technical Expertise - Provided specialized skills in machine learning and image processing for government applications');
INSERT INTO `experience` (`id`, `sort`, `title`, `organization`, `location`, `period`, `responsibilities`) VALUES (7, 7, 'IT Consultant — Owner', 'Bital IT Consulting Services', 'Perth, WA', 'Jan 2008 – Jan 2011', 'Business Analysis - Provided comprehensive business and technical analysis to diverse client base
Infrastructure Development - Developed and supported critical backup and monitoring solutions for servers and databases');
INSERT INTO `experience` (`id`, `sort`, `title`, `organization`, `location`, `period`, `responsibilities`) VALUES (8, 8, 'IT Manager', 'Submarine Systems Centre, RAN', 'Perth, WA', 'Jul 1996 – Jan 2000', 'Strategic IT Leadership - Managed comprehensive information technology infrastructure supporting submarine operations and maintenance
Executive Advisory - Provided strategic IT guidance to senior military leadership and operational boards
Organisational Impact - Delivered technology solutions that directly supported critical defence capabilities and mission readiness');
INSERT INTO `experience` (`id`, `sort`, `title`, `organization`, `location`, `period`, `responsibilities`) VALUES (9, 9, 'Project Manager — Command and Control', 'HQADF', 'Canberra, ACT', 'Jul 1993 – Dec 1996', 'Strategic Leadership - Managed development of critical military messaging systems for Australian Defence Force headquarters
Project Excellence - Successfully controlled cost, schedule, and quality across multi-year defense communications project
Cross-functional Coordination - Led technical teams and stakeholder management across multiple defence departments');
INSERT INTO `experience` (`id`, `sort`, `title`, `organization`, `location`, `period`, `responsibilities`) VALUES (10, 10, 'Analyst/Programmer — Manpower and Pay Project', 'HQADF', 'Canberra, ACT', 'Aug 1991 – Jun 1993', 'Systems Development - Designed and implemented large-scale personnel management systems for defence operations
Technical Excellence - Conducted comprehensive code reviews and built sophisticated models using CASE tools
Full-cycle Development - Led data modeling, process modeling, database design, program design, and interface design');
INSERT INTO `experience` (`id`, `sort`, `title`, `organization`, `location`, `period`, `responsibilities`) VALUES (11, 11, 'System Administrator — Manpower and Personnel', 'RAN', 'Canberra, ACT', 'Mar 1989 – Aug 1993', 'Infrastructure Management - Installed, configured, and maintained critical network and computer systems for Royal Australian Navy
Crisis Management - Executed rapid recovery procedures during system failures, ensuring minimal operational disruption
Security Operations - Maintained secure computing environments for sensitive military personnel data');

-- education
INSERT INTO `education` (`id`, `sort`, `degree`, `field`, `institution`, `year`, `thesis`) VALUES (1, 1, 'Doctor of Philosophy (PhD)', 'Computer Science', 'Curtin University', 2017, 'Feature Extraction from Multi-modal Data (GIS, Machine Learning & Computer Vision)');
INSERT INTO `education` (`id`, `sort`, `degree`, `field`, `institution`, `year`, `thesis`) VALUES (2, 2, 'Bachelor of Science (Computer Science) (Honours)', 'Computer Science', 'Curtin University', 2001, 'A Bayesian Belief Network Approach to Predicting the Prices of Australian Commonwealth Government Interest Rate Securities');
INSERT INTO `education` (`id`, `sort`, `degree`, `field`, `institution`, `year`, `thesis`) VALUES (3, 3, 'Graduate Diploma in Business', 'Business', 'Curtin University', 2000, NULL);
INSERT INTO `education` (`id`, `sort`, `degree`, `field`, `institution`, `year`, `thesis`) VALUES (4, 4, 'Bachelor of Science (Computer Science)', 'Computer Science', 'Australian National University', 1994, NULL);
INSERT INTO `education` (`id`, `sort`, `degree`, `field`, `institution`, `year`, `thesis`) VALUES (5, 5, 'Bachelor of Applied Science (Mathematics)', 'Mathematics', 'Queensland University of Technology', 1989, NULL);

-- skill
INSERT INTO `skill` (`id`, `sort`, `category`, `subcategory`, `names`) VALUES (1, 1, 'programming', 'core', 'Python, C/C++, C#, Java, JavaScript, Matlab, PHP, CSS, HTML, LaTeX, SQL, Bash');
INSERT INTO `skill` (`id`, `sort`, `category`, `subcategory`, `names`) VALUES (2, 2, 'programming', 'web', 'React, Flask, FastAPI, FastHTML, Vanilla JS, WordPress');
INSERT INTO `skill` (`id`, `sort`, `category`, `subcategory`, `names`) VALUES (3, 3, 'programming', 'ai_ml', 'Langchain, TensorFlow, PyTorch, Scikit-learn');
INSERT INTO `skill` (`id`, `sort`, `category`, `subcategory`, `names`) VALUES (4, 4, 'programming', 'educational', 'Blackboard LMS, Canvas LMS, Interactive Content Development');

-- project
INSERT INTO `project` (`id`, `sort`, `name`, `description`, `year`) VALUES (1, 1, 'Reality Reigns', 'Swipe-based decision game providing interactive fiction storytelling from fantasy adventures to educational simulations', NULL);
INSERT INTO `project` (`id`, `sort`, `name`, `description`, `year`) VALUES (2, 2, 'Talk Buddy', 'AI-based audio interface tool for conversation practice (medical diagnoses, HR discussions, English conversation)', NULL);
INSERT INTO `project` (`id`, `sort`, `name`, `description`, `year`) VALUES (3, 3, 'Curriculum Curator', 'AI-based tool for creating, managing and curating learning materials based on unique teaching philosophies', NULL);
INSERT INTO `project` (`id`, `sort`, `name`, `description`, `year`) VALUES (4, 4, 'Feed Forward System', 'AI-based assessment feedback tool for various assessment types', NULL);
INSERT INTO `project` (`id`, `sort`, `name`, `description`, `year`) VALUES (5, 5, 'Student Feedback Analyzer', 'AI tool that analyzes student feedback forms to suggest course improvements', NULL);

-- achievement
INSERT INTO `achievement` (`id`, `sort`, `achievement_text`) VALUES (1, 1, 'Teaching Excellence - 85.0% average student rating across 38 unit deliveries since 2019, with 16 deliveries scoring 100% and all six survey dimensions at or above 80%');
INSERT INTO `achievement` (`id`, `sort`, `achievement_text`) VALUES (2, 2, 'Research Funding - Lead Investigator on the AUD $20,000 Curtin Needs-Based Funding (Learning & Teaching) Grant 2026, awarded on an evidence base of 14,973 logged student-AI interactions; technical co-lead on the Assessment 2030 Future Fund (AUD $10,560, 2025)');
INSERT INTO `achievement` (`id`, `sort`, `achievement_text`) VALUES (3, 3, 'Research Outputs - Accepted ACIS 2026 (solo) and ASCILITE 2026 (contributing) papers, with a sustained program of AI-in-education scholarship and invited research seminars');
INSERT INTO `achievement` (`id`, `sort`, `achievement_text`) VALUES (4, 4, 'Course Leadership - Led the repositioning of the Master of Information Systems and Technology into a standalone degree, growing it ~6x to 110 EFTSL (2025) and 148 EFTSL year-to-date (2026); secured Australian Computer Society accreditation');
INSERT INTO `achievement` (`id`, `sort`, `achievement_text`) VALUES (5, 5, 'Curriculum Innovation - Redesigned 8 units for the AI era and built 2 new postgraduate units from scratch, delivering a 12% average pass-rate uplift');
INSERT INTO `achievement` (`id`, `sort`, `achievement_text`) VALUES (6, 6, 'Assessment Innovation - Created CloudCore Networks, selected by Curtin''s Assessment 2030 as a Lane 2 (AI-robust) exemplar, and the foundation for WorkReady under the $735,000 WIL-Ignite project');
INSERT INTO `achievement` (`id`, `sort`, `achievement_text`) VALUES (7, 7, 'Executive Education - Designed and delivered 5 AI courses to ~190 participants across 6 sessions (4.3/5 satisfaction), profiled in the Australian Financial Review alongside Bond and Melbourne');
INSERT INTO `achievement` (`id`, `sort`, `achievement_text`) VALUES (8, 8, 'Open Educational Resources - 30+ free apps and the ''Learning with AI'' open-textbook series (4 core books + domain companions, 1,400+ monthly downloads); 2 titles adopted as e-readings by Kaplan Business School, and the Curriculum Curator tool adopted as the foundation of FLUX');
INSERT INTO `achievement` (`id`, `sort`, `achievement_text`) VALUES (9, 9, 'Discipline Recognition - Invited to the FBL Advisory Board, the Curtin Future of Work Institute, and the Curtin Festival of AI; peer-reviewer for ACIS since 2023');
INSERT INTO `achievement` (`id`, `sort`, `achievement_text`) VALUES (10, 10, 'Professional Standing - Certified Professional Member of the Australian Computer Society (ACS); led the discipline''s accreditation and international articulation (SCNU) agenda');

-- publication
INSERT INTO `publication` (`id`, `sort`, `kind`, `title`, `authors`, `year`, `venue`, `description`, `license`) VALUES (1, 1, 'book', 'Conversation, Not Delegation: How to Think With AI, Not Just Use It', NULL, NULL, NULL, 'Book 1 (the method). Foundational methodology: the Conversation Loop, VET, cognitive traps, and AI Last. Two titles in the series adopted as e-readings by Kaplan Business School', 'Self-published; free online, KDP print/ISBN');
INSERT INTO `publication` (`id`, `sort`, `kind`, `title`, `authors`, `year`, `venue`, `description`, `license`) VALUES (2, 2, 'book', 'The Human Edge: Using AI with Judgement', NULL, NULL, NULL, 'Book 2 (the practice). Trust, brief, check, deliver - professional judgement for everyday work when everyone has the same tools', 'Self-published; free online, KDP print/ISBN');
INSERT INTO `publication` (`id`, `sort`, `kind`, `title`, `authors`, `year`, `venue`, `description`, `license`) VALUES (3, 3, 'book', 'Speak Software: Programming at the Natural-Language Layer', NULL, NULL, NULL, 'Book 3 (the build). You describe, an agent builds, and you decide whether it is true - specification, guardrails, and verification', 'Self-published; free online');
INSERT INTO `publication` (`id`, `sort`, `kind`, `title`, `authors`, `year`, `venue`, `description`, `license`) VALUES (4, 4, 'book', 'Model Data, Verify AI: Relational Design and SQL in the AI Era', NULL, NULL, NULL, 'Book 4 (the data). Model the data, prove the queries, change the schema without gambling - the data layer when AI writes the SQL', 'Self-published; free online');
INSERT INTO `publication` (`id`, `sort`, `kind`, `title`, `authors`, `year`, `venue`, `description`, `license`) VALUES (5, 5, 'book', 'The ''Learning with AI'' series (companions)', NULL, NULL, NULL, 'Companion volumes apply the core method across programming (Think/Code/Converse/Ship Python, Build Web), security and networking, and education - 20+ open textbooks in total, all free to read online', 'Self-published; free online, KDP print/ISBN');
INSERT INTO `publication` (`id`, `sort`, `kind`, `title`, `authors`, `year`, `venue`, `description`, `license`) VALUES (6, 6, 'conference', 'Use of multiple low level features to find interesting regions', 'Borck, M., G. West, and T. Tan', 2014, 'ICPRAM 2014', NULL, NULL);
INSERT INTO `publication` (`id`, `sort`, `kind`, `title`, `authors`, `year`, `venue`, `description`, `license`) VALUES (7, 7, 'conference', 'Using depth maps to find interesting regions', 'Borck, M., R. Palmer, G. West, and T. Tan', 2014, '2014 IEEE Region 10 Symposium (TENSYMP 2014)', NULL, NULL);
INSERT INTO `publication` (`id`, `sort`, `kind`, `title`, `authors`, `year`, `venue`, `description`, `license`) VALUES (8, 8, 'conference', 'An image engineering approach to analysing mobile mapping data', 'Borck, M., G. West, and T. Tan', 2014, 'Research at Locate''14', NULL, NULL);
INSERT INTO `publication` (`id`, `sort`, `kind`, `title`, `authors`, `year`, `venue`, `description`, `license`) VALUES (9, 9, 'conference', 'Intensity and Range Based Features for Object Detection in Mobile Mapping Data', 'Palmer, R., M. Borck, G. West, and T. Tan', 2012, 'XXII ISPRS Congress, ISPRS 2012', NULL, NULL);
INSERT INTO `publication` (`id`, `sort`, `kind`, `title`, `authors`, `year`, `venue`, `description`, `license`) VALUES (10, 10, 'conference', 'Industrial Application of Sensor Nets', 'Borck, M.', 2000, 'Computer', NULL, NULL);
INSERT INTO `publication` (`id`, `sort`, `kind`, `title`, `authors`, `year`, `venue`, `description`, `license`) VALUES (11, 11, 'conference', 'Cognitive Strategy Transfer: Why Human Complexity-Management Strategies Improve Large Language Model Performance', 'Borck, M.', 2026, 'ACIS 2026 (Australasian Conference on Information Systems)', NULL, NULL);
INSERT INTO `publication` (`id`, `sort`, `kind`, `title`, `authors`, `year`, `venue`, `description`, `license`) VALUES (12, 12, 'conference', 'Designing AI-mediated interactive learning environments for communication skills: Insights from two implementations', 'Cocks, N., B. Lush, I. MacKenzie, E. Calton, P. Simpson, C. Fernandes, J. Beilby, M. Low, M. Borck, A. Angus, M. Reed, M. Jopia Vilches, and S. Raghav', 2026, 'ASCILITE 2026 (Australasian Society for Computers in Learning in Tertiary Education)', NULL, NULL);
INSERT INTO `publication` (`id`, `sort`, `kind`, `title`, `authors`, `year`, `venue`, `description`, `license`) VALUES (13, 13, 'thesis', 'Feature Extraction from Multi-modal Data', NULL, 2017, 'GIS, Machine Learning & Computer Vision', 'Investigates feature extraction methods for imagery and depth data of urban transport corridors from vehicle-based mobile mapping systems', NULL);
INSERT INTO `publication` (`id`, `sort`, `kind`, `title`, `authors`, `year`, `venue`, `description`, `license`) VALUES (14, 14, 'honour', 'A Bayesian Belief Network Approach to Predicting the Prices of Australian Commonwealth Government Interest Rate Securities', NULL, 2001, 'School of Computing, Curtin University', NULL, NULL);

-- grant
INSERT INTO `grant` (`id`, `sort`, `title`, `scheme`, `funder`, `role`, `amount`, `year`, `summary`) VALUES (1, 1, 'Scaffolding AI Interaction: A Low-Cost Intervention for Equitable Student Outcomes', 'Curtin Needs-Based Funding (Learning & Teaching) Grant', 'Curtin University (LITEC)', 'Lead Investigator (CI)', 'AUD $20,000', 2026, 'A four-unit controlled trial with pre-registered equity measures, testing whether a low-cost conversational prompt raises the quality of student-AI interaction and lifts outcomes for low-SES and first-in-family students. Co-investigators: Moraes, Reiners, Ralph.');
INSERT INTO `grant` (`id`, `sort`, `title`, `scheme`, `funder`, `role`, `amount`, `year`, `summary`) VALUES (2, 2, 'Assessment 2030 Future Fund — AI Digital-Human Pilot', 'Assessment 2030 Future Fund', 'Curtin University', 'Technical Co-Lead (Lead: Dr Sonia Raghav)', 'AUD $10,560', 2025, 'An AI digital-human pilot building oral-communication confidence in a large core Management unit; a cross-disciplinary collaboration with Management colleagues.');

-- certification
INSERT INTO `certification` (`id`, `sort`, `name`, `year`) VALUES (1, 1, 'Google AI Course', 2024);
INSERT INTO `certification` (`id`, `sort`, `name`, `year`) VALUES (2, 2, 'Microsoft AI Course', 2024);
INSERT INTO `certification` (`id`, `sort`, `name`, `year`) VALUES (3, 3, 'Cyber Security Training', 2021);
INSERT INTO `certification` (`id`, `sort`, `name`, `year`) VALUES (4, 4, 'Ethics Reviewer Training', 2021);
INSERT INTO `certification` (`id`, `sort`, `name`, `year`) VALUES (5, 5, 'Equal Opportunity Work Essentials', 2021);
INSERT INTO `certification` (`id`, `sort`, `name`, `year`) VALUES (6, 6, 'HDR Supervisors Update', 2020);
INSERT INTO `certification` (`id`, `sort`, `name`, `year`) VALUES (7, 7, 'Curtin Research Integrity', 2020);
INSERT INTO `certification` (`id`, `sort`, `name`, `year`) VALUES (8, 8, 'Provide Advanced First Aid', '2012–2019');

-- service
INSERT INTO `service` (`id`, `sort`, `category`, `role`, `organization`, `project`, `year`, `period`) VALUES (1, 1, 'profession', 'Conference Paper Reviewer', 'Australian Conference on Information Systems (International)', NULL, 2019, NULL);
INSERT INTO `service` (`id`, `sort`, `category`, `role`, `organization`, `project`, `year`, `period`) VALUES (2, 2, 'profession', 'Conference Paper Reviewer', 'Australian Conference on Information Systems (International)', NULL, '2023, 2024, 2025, 2026', NULL);
INSERT INTO `service` (`id`, `sort`, `category`, `role`, `organization`, `project`, `year`, `period`) VALUES (3, 3, 'community', 'Lead Developer', NULL, 'Image Processing for Orange', NULL, '2015-2019');
INSERT INTO `service` (`id`, `sort`, `category`, `role`, `organization`, `project`, `year`, `period`) VALUES (4, 4, 'community', 'User Contribution', NULL, 'Graph Merging for Scikit Image', 2015, NULL);
INSERT INTO `service` (`id`, `sort`, `category`, `role`, `organization`, `project`, `year`, `period`) VALUES (5, 5, 'community', 'User Contribution', NULL, 'User Guide, Image Annotation Tool', 2014, NULL);

-- membership
INSERT INTO `membership` (`id`, `sort`, `organization`, `status`, `year`, `note`) VALUES (1, 1, 'Australian Computer Society (ACS)', 'Certified Professional', 2011, NULL);

-- interest
INSERT INTO `interest` (`id`, `sort`, `name`) VALUES (1, 1, 'Karate');
INSERT INTO `interest` (`id`, `sort`, `name`) VALUES (2, 2, 'Muay Thai');
INSERT INTO `interest` (`id`, `sort`, `name`) VALUES (3, 3, 'Krav Maga');
INSERT INTO `interest` (`id`, `sort`, `name`) VALUES (4, 4, 'Atari 2600 Programming');
INSERT INTO `interest` (`id`, `sort`, `name`) VALUES (5, 5, 'RetroVerse Studios (indie game studio)');
INSERT INTO `interest` (`id`, `sort`, `name`) VALUES (6, 6, 'Astronomy');
INSERT INTO `interest` (`id`, `sort`, `name`) VALUES (7, 7, 'Photography');

-- teaching_satisfaction
INSERT INTO `teaching_satisfaction` (`id`, `sort`, `metric`, `details`) VALUES (1, 1, '85.0% average student rating', 'Across 38 unit deliveries since 2019 (eVALUate to 2022, Insight from 2023); all six survey dimensions at or above 80% - Assessments 89.2%, Engagement 86.8%, Expectations 85.5%, Resources 84.9%, Support 81.2%');
INSERT INTO `teaching_satisfaction` (`id`, `sort`, `metric`, `details`) VALUES (2, 2, '16 deliveries at 100%', 'Top results sustained across 8 units, alongside a 12% average pass-rate uplift in AI-redesigned units and a return to 100% in Semester 2 2025 after the 2024 AI transition');
INSERT INTO `teaching_satisfaction` (`id`, `sort`, `metric`, `details`) VALUES (3, 3, 'Full-span teaching reach', 'Undergraduate, postgraduate and executive education - a range few academics deliver across - online and on-campus, domestic and international (China), from small specialist classes to cohorts of 300');

-- teaching_innovation
INSERT INTO `teaching_innovation` (`id`, `sort`, `name`, `description`) VALUES (1, 1, 'Cloud Core Simulation', 'Created complete virtual company with IT infrastructure, policies, and staff chatbot for authentic audit experiences');
INSERT INTO `teaching_innovation` (`id`, `sort`, `name`, `description`) VALUES (2, 2, 'Real-World Integration', 'Students report assessments prepare them for ''workplace environment''');
INSERT INTO `teaching_innovation` (`id`, `sort`, `name`, `description`) VALUES (3, 3, 'Student Impact', 'The environment created while performing the assignment is nothing less than working in real-time');
