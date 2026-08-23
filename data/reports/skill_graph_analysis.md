# RouteMaster - Skill Dependency Graph Analysis Report

Generated dynamically. Local time: 2026-08-22

## 1. Network Metrics Summary

- **Total Nodes**: 8908 (skills)
- **Total Edges**: 286 (dependencies)
- **Foundational / Root Skills**: 29
- **Advanced / Leaf Skills**: 198
- **Orphan Skills (Isolated)**: 8612
- **Connected Graph Components**: 18 (excluding isolated orphans)
- **Cycles Detected**: 0
- **Maximum Dependency Depth**: 5
- **Average Dependency Depth**: 0.04

## 2. Foundational / Root Skills

These skills have outgoing dependencies but no incoming prerequisites. They represent the starting points of learning paths:

| Skill ID | Skill Name | Category | Out-Degree |
| --- | --- | --- | --- |
| `SK_00002` | 3D Modeling | AR/VR | 5 |
| `SK_00010` | Algorithms | Game Development | 1 |
| `SK_00070` | C | Embedded Systems | 3 |
| `SK_00079` | Circuit Design | Electronics | 1 |
| `SK_00082` | Cloud Computing | Cloud | 4 |
| `SK_00105` | Cryptography | Cloud | 5 |
| `SK_00111` | Dart | Mobile Development | 1 |
| `SK_00122` | Data Warehousing | Data Engineering | 3 |
| `SK_00140` | Digital Electronics | Electronics | 3 |
| `SK_00167` | ETL | Data Engineering | 1 |
| `SK_00212` | HTML | Software Engineering | 1 |
| `SK_00213` | HTML/CSS | Frontend Development | 3 |
| `SK_00239` | Java | Mobile Development | 5 |
| `SK_00249` | Kotlin | Mobile Development | 3 |
| `SK_00257` | Linux | Systems | 8 |
| `SK_00270` | Mathematics | AI/ML | 1 |
| `SK_00306` | Network Troubleshooting | Cybersecurity | 2 |
| `SK_00308` | Networking Protocols | IoT | 1 |
| `SK_00315` | NoSQL | Database | 6 |
| `SK_00320` | Object-Oriented Programming | Software Engineering | 2 |

*...and 9 more roots.*

## 3. Advanced / Leaf Skills

These skills represent the final goals of existing dependency chains, with no further outgoing prerequisite edges:

| Skill ID | Skill Name | Category | In-Degree |
| --- | --- | --- | --- |
| `SK_00003` | A/B Testing | Data Science | 1 |
| `SK_00004` | A/B Testing (UX) | UI/UX | 1 |
| `SK_00007` | Adobe XD | UI/UX | 1 |
| `SK_00011` | Altium | Electronics | 1 |
| `SK_00012` | Amazon API Gateway | Cloud | 1 |
| `SK_00013` | Amazon DynamoDB | Cloud | 1 |
| `SK_00014` | Amazon RDS | Cloud | 1 |
| `SK_00015` | Amazon Redshift | Data Engineering | 1 |
| `SK_00018` | Android Studio | Mobile Development | 1 |
| `SK_00019` | Angular | Frontend | 1 |
| `SK_00021` | Ansible | DevOps | 2 |
| `SK_00022` | Apache Airflow | Data Engineering | 1 |
| `SK_00023` | Apache Kafka | Data Engineering | 1 |
| `SK_00026` | API Gateway | Architecture | 1 |
| `SK_00029` | Appium | QA | 1 |
| `SK_00032` | Arduino | Embedded Systems | 1 |
| `SK_00033` | ArgoCD | DevOps | 2 |
| `SK_00036` | ARM Cortex | Embedded Systems | 1 |
| `SK_00043` | Auto Layout | UI/UX | 1 |
| `SK_00047` | AWS CloudFormation | Cloud | 1 |

*...and 178 more leaves.*

## 4. Skills with Highest Downstream Impact

Impact is measured by the total number of skills that transitively depend on this skill (prerequisite closure size):

| Skill ID | Skill Name | Direct Dependents | Downstream Impact (Transitive) |
| --- | --- | --- | --- |
| `SK_00360` | Python | 12 | 27 |
| `SK_00212` | HTML | 1 | 17 |
| `SK_00106` | CSS | 1 | 16 |
| `SK_00070` | C | 3 | 15 |
| `SK_00082` | Cloud Computing | 4 | 15 |
| `SK_00105` | Cryptography | 5 | 15 |
| `SK_00240` | JavaScript | 11 | 15 |
| `SK_00270` | Mathematics | 1 | 15 |
| `SK_00264` | Machine Learning | 5 | 14 |
| `SK_00306` | Network Troubleshooting | 2 | 14 |
| `SK_00305` | Network Security | 6 | 12 |
| `SK_00257` | Linux | 8 | 11 |
| `SK_00066` | Blockchain | 7 | 10 |
| `SK_00156` | Embedded C | 3 | 10 |
| `SK_00132` | Deep Learning | 5 | 8 |

## 5. Most Depended-Upon Skills (Direct Out-Degree)

These skills are direct prerequisites for the largest number of immediate target skills:

| Skill ID | Skill Name | Direct Out-Degree | Transitive Dependents |
| --- | --- | --- | --- |
| `SK_00360` | Python | 12 | 27 |
| `SK_00240` | JavaScript | 11 | 15 |
| `SK_00435` | SQL | 11 | 8 |
| `SK_00046` | Amazon Web Services | 9 | 4 |
| `SK_00257` | Linux | 8 | 11 |
| `SK_00066` | Blockchain | 7 | 10 |
| `SK_00277` | Microcontrollers | 7 | 8 |
| `SK_00429` | Solidity | 7 | 5 |
| `SK_00044` | Automated Testing | 6 | 3 |
| `SK_00280` | Microsoft Azure | 6 | 3 |
| `SK_00305` | Network Security | 6 | 12 |
| `SK_00315` | NoSQL | 6 | 6 |
| `SK_00450` | System Design | 6 | 8 |
| `SK_00002` | 3D Modeling | 5 | 3 |
| `SK_00105` | Cryptography | 5 | 15 |

