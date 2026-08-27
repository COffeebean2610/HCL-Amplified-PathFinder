# RouteMaster - Data Profiling Report (Raw Datasets)

Generated dynamically. Local time: 2026-08-22

This profiling report analyzes the structure, metrics, columns, and quality anomalies of the raw datasets.

## Executive Summary

| Dataset Name | Row Count | Column Count | Duplicate Rows | Anomalies Detected |
| --- | --- | --- | --- | --- |
| Career-Interest Dataset | 241 | 9 | 0 | 1 |
| Career-Technical Skills Dataset | 608 | 9 | 0 | 0 |
| Career-Transferable Skills Dataset | 453 | 8 | 0 | 1 |
| Coursera Courses Dataset | 3522 | 7 | 98 | 3 |
| Engineering Projects Dataset | 251 | 9 | 0 | 0 |
| Skill Dependency / Prerequisite Dataset | 287 | 8 | 0 | 1 |

---

## Dataset: Career-Interest Dataset

- **File Path**: `data/raw\Career–Interest Dataset.csv`
- **Rows**: 241
- **Columns**: 9
- **Duplicate Rows**: 0

### Data Quality Anomalies

- ⚠️ Found unexpected columns: ['Unnamed: 7', 'Unnamed: 8']

### Column Details

| Column Name | Data Type | Null Count | Null % | Unique Values | Sample Values |
| --- | --- | --- | --- | --- | --- |
| career\_id | str | 0 | 0.0% | 80 | `'CAR001'`, `'CAR001'`, `'CAR001'` |
| career\_title | str | 0 | 0.0% | 80 | `'AI Engineer'`, `'AI Engineer'`, `'AI Engineer'` |
| career_domain | str | 0 | 0.0% | 19 | `'Artificial Intelligence'`, `'Artificial Intelligence'`, `'Artificial Intelligence'` |
| interest\_type | str | 0 | 0.0% | 6 | `'Investigative'`, `'Realistic'`, `'Conventional'` |
| interest\_score | float64 | 0 | 0.0% | 20 | `'4.9'`, `'3.8'`, `'3.4'` |
| interest\_description | str | 0 | 0.0% | 241 | `'Requires strong interest in research and solving complex algorithms.'`, `'Involves practical implementation of AI models into production environments.'`, `'Requires structured data management and organized code repositories.'` |
| career\_description | str | 0 | 0.0% | 80 | `'AI Engineers design and deploy artificial intelligence systems using machine learning and deep learning.'`, `'AI Engineers design and deploy artificial intelligence systems using machine learning and deep learning.'`, `'AI Engineers design and deploy artificial intelligence systems using machine learning and deep learning.'` |
| Unnamed: 7 | str | 238 | 98.8% | 1 | `'images'`, `'images'`, `'images'` |
| Unnamed: 8 | str | 238 | 98.8% | 1 | `'or code.'`, `'or code.'`, `'or code.'` |

---

## Dataset: Career-Technical Skills Dataset

- **File Path**: `data/raw\CAREER–TECHNICAL SKILLS DATASET.csv`
- **Rows**: 608
- **Columns**: 9
- **Duplicate Rows**: 0

### Data Quality Anomalies

- ✅ No structural anomalies detected.

### Column Details

| Column Name | Data Type | Null Count | Null % | Unique Values | Sample Values |
| --- | --- | --- | --- | --- | --- |
| career_id | str | 0 | 0.0% | 60 | `'CAR001'`, `'CAR001'`, `'CAR001'` |
| career_title | str | 0 | 0.0% | 55 | `'AI Engineer'`, `'AI Engineer'`, `'AI Engineer'` |
| skill_id | str | 0 | 0.0% | 233 | `'SK001'`, `'SK002'`, `'SK003'` |
| skill_name | str | 0 | 0.0% | 216 | `'Python'`, `'Machine Learning'`, `'Deep Learning'` |
| skill_category | str | 0 | 0.0% | 26 | `'Programming'`, `'AI/ML'`, `'AI/ML'` |
| importance | str | 0 | 0.0% | 3 | `'Critical'`, `'Critical'`, `'Critical'` |
| in_demand | str | 0 | 0.0% | 2 | `'Yes'`, `'Yes'`, `'Yes'` |
| hot_technology | str | 0 | 0.0% | 2 | `'Yes'`, `'Yes'`, `'Yes'` |
| description | str | 0 | 0.0% | 230 | `'General-purpose programming language widely used for AI, machine learning, and backend development.'`, `'Methods for building systems that learn patterns from data and make predictions.'`, `'Machine learning approach based on multi-layer neural networks for complex data tasks.'` |

---

## Dataset: Career-Transferable Skills Dataset

- **File Path**: `data/raw\CAREER–TRANSFERABLE SKILLS DATASET.csv`
- **Rows**: 453
- **Columns**: 8
- **Duplicate Rows**: 0

### Data Quality Anomalies

- ⚠️ First row contains duplicated header labels.

### Column Details

| Column Name | Data Type | Null Count | Null % | Unique Values | Sample Values |
| --- | --- | --- | --- | --- | --- |
| career_id | str | 0 | 0.0% | 66 | `'career_id'`, `'CAR061'`, `'CAR061'` |
| career_title | str | 0 | 0.0% | 66 | `'career_title'`, `'IT Director'`, `'IT Director'` |
| skill_id | str | 0 | 0.0% | 21 | `'skill_id'`, `'TSK016'`, `'TSK020'` |
| skill_name | str | 0 | 0.0% | 21 | `'skill_name'`, `'Leadership'`, `'Strategic Thinking'` |
| skill_category | str | 0 | 0.0% | 11 | `'skill_category'`, `'Leadership'`, `'Cognitive'` |
| importance_score | str | 0 | 0.0% | 13 | `'importance_score'`, `'4.9'`, `'4.8'` |
| data_value | str | 0 | 0.0% | 4 | `'data_value'`, `'Critical'`, `'Critical'` |
| description | str | 0 | 0.0% | 453 | `'description'`, `"Essential for guiding the IT department's strategic vision and managing technical teams."`, `'Crucial for aligning technology initiatives with long-term business objectives.'` |

---

## Dataset: Coursera Courses Dataset

- **File Path**: `data/raw\coursera_courses.csv`
- **Rows**: 3522
- **Columns**: 7
- **Duplicate Rows**: 98

### Data Quality Anomalies

- ⚠️ Column 'Difficulty Level' has unusual difficulty values: ['Not Calibrated', 'Conversant']
- ⚠️ Column 'Course Rating' contains non-numeric ratings: ['Not Calibrated']
- ⚠️ Column 'Skills' uses double spaces (2+ spaces) as separators. No commas found.

### Column Details

| Column Name | Data Type | Null Count | Null % | Unique Values | Sample Values |
| --- | --- | --- | --- | --- | --- |
| Course Name | str | 0 | 0.0% | 3416 | `'Write A Feature Length Screenplay For Film Or Television'`, `'Business Strategy: Business Model Canvas Analysis with Miro'`, `'Silicon Thin Film Solar Cells'` |
| University | str | 0 | 0.0% | 184 | `'Michigan State University'`, `'Coursera Project Network'`, `'�cole Polytechnique'` |
| Difficulty Level | str | 0 | 0.0% | 5 | `'Beginner'`, `'Beginner'`, `'Advanced'` |
| Course Rating | str | 0 | 0.0% | 31 | `'4.8'`, `'4.8'`, `'4.1'` |
| Course URL | str | 0 | 0.0% | 3424 | `'https://www.coursera.org/learn/write-a-feature-length-screenplay-for-film-or-television'`, `'https://www.coursera.org/learn/canvas-analysis-miro'`, `'https://www.coursera.org/learn/silicon-thin-film-solar-cells'` |
| Course Description | str | 0 | 0.0% | 3397 | `'Write a Full Length Feature Film Script  In this course, you will write a complete, feature-length screenplay for film or television, be it a serious drama or romantic comedy or anything in between. You�ll learn to break down the creative process into components, and you�ll discover a structured process that allows you to produce a polished and pitch-ready script by the end of the course. Completing this project will increase your confidence in your ideas and abilities, and you�ll feel prepared to pitch your first script and get started on your next. This is a course designed to tap into your creativity and is based in "Active Learning". Most of the actual learning takes place within your own activities - that is, writing! You will learn by doing.  Here is a link to a TRAILER for the course. To view the trailer, please copy and paste the link into your browser. https://vimeo.com/382067900/b78b800dc0  Learner review: "Love the approach Professor Wheeler takes towards this course. It\'s to the point, easy to follow, and very informative! Would definitely recommend it to anyone who is interested in taking a Screenplay Writing course!  The course curriculum is simple: We will adopt a professional writers room process in which you�ll write, post your work for peer review, share feedback with your peers and revise your work with the feedback you receive from your peers. That\'s how we do it in the real world. You will feel as if you were in a professional writers room yet no prior experience as a writer is required. I\'m a proponent of Experiential Learning (Active Learning). My lectures are short (sometimes just two minutes long) and to the point, designed in a step-by-step process essential to your success as a script writer. I will guide you but I won�t "show" you how to write. I firmly believe that the only way to become a writer is to write, write, write.  Learner Review: "I would like to thank this course instructor. It\'s an amazing course"  What you�ll need to get started: As mentioned above, no prior script writing experience is required. To begin with, any basic word processor will do. During week two, you can choose to download some free scriptwriting software such as Celtx or Trelby or you may choose to purchase Final Draft, the industry standard, or you can continue to use your word processor and do your own script formatting.   Learner Review: "Now I am a writer!"  If you have any concerns regarding the protection of your original work, Coursera\'s privacy policy protects the learner\'s IP and you are indeed the sole owners of your work.'`, `'By the end of this guided project, you will be fluent in identifying and creating Business Model Canvas solutions based on previous high-level analyses and research data.  This will enable you to identify and map the elements required for new products and services. Furthermore, it is essential for generating positive results for your business venture. This guided project is designed to engage and harness your visionary and exploratory abilities. You will use proven models in strategy and product development with the Miro platform to explore and analyse your business propositions.   We will practice critically examining results from previous analysis and research results in deriving the values for each of the business model sections.'`, `'This course consists of a general presentation of solar cells based on silicon thin films.   It is the third MOOC of the photovoltaic series of Ecole polytechnique on Coursera. The general aspects of the photovoltaic field are treated in "Photovoltaic Solar Energy". And the detailed description of the crystalline silicon solar cells can be found in "Physics of Silicon Solar Cells".  After a brief presentation of solar cells operation, thin film semiconductors are described here. The general properties of disordered and crystalline semiconductors are found very different, in particular in terms of band structure and doping mechanisms. Silicon thin films, generally less than 1 �m thick, are deposited from silane plasma leading to hydrogen incorporation. The growth mechanisms are discussed, in particular the capability to prepare partially crystallized thin films which appear as a mixture of nanocrystallites embedded in an amorphous tissue.  The consequences of the semiconductor properties on solar cells behavior are reviewed. The optical properties of amorphous and nanocrystalline silicon are complementary. Thus the plasma process is particularly well adapted to the preparation of multijunctions, with conversion efficiencies around 13-15 %. Furthermore plasma processes allow to prepare solar cells in large area on glass or flexible substrates.  Finally, it is shown that crystalline and amorphous silicon materials can be combine into heterojunctions solar cells with high efficiency conversion (about 25 %).  **This course is part of a series of 3** Photovoltaic solar energy (https://www.coursera.org/learn/photovoltaic-solar-energy/) Physics of silicon solar cells (https://www.coursera.org/learn/physics-silicon-solar-cells/) Silicon thin film solar cells'` |
| Skills | str | 0 | 0.0% | 3424 | `'Drama  Comedy  peering  screenwriting  film  Document Review  dialogue  creative writing  Writing  unix shells arts-and-humanities music-and-art'`, `'Finance  business plan  persona (user experience)  business model canvas  Planning  Business  project  Product Development  presentation  Strategy business business-strategy'`, `'chemistry  physics  Solar Energy  film  lambda calculus  Electrical Engineering  electronics  energy  silicon  thinning physical-science-and-engineering electrical-engineering'` |

---

## Dataset: Engineering Projects Dataset

- **File Path**: `data/raw\Engineering Projects Dataset.csv`
- **Rows**: 251
- **Columns**: 9
- **Duplicate Rows**: 0

### Data Quality Anomalies

- ✅ No structural anomalies detected.

### Column Details

| Column Name | Data Type | Null Count | Null % | Unique Values | Sample Values |
| --- | --- | --- | --- | --- | --- |
| project_id | str | 0 | 0.0% | 251 | `'PROJ001'`, `'PROJ002'`, `'PROJ003'` |
| project_name | str | 0 | 0.0% | 251 | `'LMS Platform (Udemy Clone)'`, `'Online Course Platform'`, `'Student Portal System'` |
| domain | str | 0 | 0.0% | 7 | `'Software Engineering'`, `'Software Engineering'`, `'Database Management'` |
| skills | str | 0 | 0.0% | 230 | `'JavaScript, React, Authentication, REST APIs, Database Design'`, `'React, JavaScript, REST APIs, Authentication, Database Design'`, `'JavaScript, CRUD Operations, Database Design, Authentication, SQL'` |
| tech_stack | str | 0 | 0.0% | 150 | `'React, Node.js, Express.js, MongoDB'`, `'React, Node.js, Express.js, MongoDB'`, `'React, Node.js, Express.js, MySQL'` |
| description | str | 0 | 0.0% | 251 | `'An online learning platform where instructors publish courses and students enroll, learn, and track course progress.'`, `'A web platform for delivering structured online courses, managing learners, and organizing educational content.'`, `'A student information system for managing profiles, academic records, courses, and administrative information.'` |
| difficulty | str | 0 | 0.0% | 3 | `'Advanced'`, `'Intermediate'`, `'Intermediate'` |
| github_url | str | 7 | 2.8% | 241 | `'https://github.com/antonioerdeljac/next13-1ms-platform'`, `'https://github.com/PacktPublishing/MERN-Stack-Course'`, `'https://github.com/mkkhedawat/student-management-system'` |
| tags | str | 0 | 0.0% | 250 | `'LMS, E-Learning, Courses, MERN'`, `'Education, Courses, LMS'`, `'Student, Portal, Database, Education'` |

---

## Dataset: Skill Dependency / Prerequisite Dataset

- **File Path**: `data/raw\Skill Dependency _ Prerequisite Dataset.csv`
- **Rows**: 287
- **Columns**: 8
- **Duplicate Rows**: 0

### Data Quality Anomalies

- ⚠️ Column 'difficulty' has unusual difficulty values: ['Column 7']

### Column Details

| Column Name | Data Type | Null Count | Null % | Unique Values | Sample Values |
| --- | --- | --- | --- | --- | --- |
| source_skill_id | str | 0 | 0.0% | 97 | `'SK516'`, `'SK516'`, `'SK046'` |
| source_skill | str | 0 | 0.0% | 99 | `'C'`, `'C'`, `'HTML'` |
| target_skill_id | str | 0 | 0.0% | 267 | `'SK106'`, `'SK575'`, `'SK047'` |
| target_skill | str | 0 | 0.0% | 268 | `'C++'`, `'Rust'`, `'CSS'` |
| relationship | str | 0 | 0.0% | 4 | `'prerequisite'`, `'recommended_prerequisite'`, `'prerequisite'` |
| reason | str | 0 | 0.0% | 287 | `'C provides the foundational procedural programming concepts required to learn object-oriented C++.'`, `"Understanding memory management in C helps developers grasp Rust's ownership and borrowing concepts."`, `'HTML provides the structure of web pages, which is necessary before applying styles with CSS.'` |
| difficulty | str | 0 | 0.0% | 4 | `'Beginner'`, `'Intermediate'`, `'Beginner'` |
| domain | str | 0 | 0.0% | 29 | `'Programming'`, `'Programming'`, `'Frontend'` |

---

