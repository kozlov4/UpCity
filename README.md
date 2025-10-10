# 🏙️ UpCity
<p align="center">
  <img src="https://i.ibb.co/RkGP9xgp/image-removebg-preview-1.png" width="300" alt="Project Logo">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="Backend: FastAPI">
  <img src="https://img.shields.io/badge/Frontend-React-61DAFB?style=for-the-badge&logo=react&logoColor=white" alt="Frontend: React">
  <img src="https://img.shields.io/badge/Database-PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white" alt="Database: PostgreSQL">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License: MIT">
</p>



---
## 📚 Table of Contents
- [About the Project](#about-the-project)
- [Major Features](#major-features)
- [Preview / User Flow](#preview-user-flow)
- [Demo Video](#demo-video)
- [Project Architecture](#project-architecture)
- [Tech Stack](#tech-stack)
- [Documentation](#documentation)
- [Developers](#developers)
- [License](#license)

---


<a id="about-the-project"></a>
## 🌆 About the Project

**UpCity** is a modern web platform that makes city life more efficient and comfortable.  
It connects **citizens, municipal services, and administrators** in one digital space.

💡 Citizens can mark issues on the map (broken lights, potholes, waste problems, etc.).  
🏙️ Municipal services respond and fix them.  
🧑‍💼 Administrators manage users, verify reports, and track progress.

> The platform builds transparency and collaboration between citizens and local authorities —  
> for a cleaner, smarter, and safer city.

---

<a id="major-features"></a>
## ✨ Major Features

**UpCity** is an integrated city management platform that connects **citizens**, **administrators**, and **municipal services** in one digital ecosystem — making urban problem-solving faster, smarter, and more transparent.

---

### 👥 For Citizens (Frontend / Mobile)

- 📝 **Create a Report** — submit an issue (e.g., pothole, broken light, waste) with a photo, description, and geolocation.  
- 🗺️ **Interactive City Map** — view all reports with filtering by category, status, or location.  
- 📋 **Track Report Status** — monitor your submitted reports and receive updates (“In Progress”, “Resolved”).  
- 🔔 **Automatic Notifications** — get alerts about report status changes or important updates.  
- 💬 **Secure Registration & Login** — sign up via email or Google account (Facebook integration in future release).  
- 🌟 **Premium Subscription** *(optional)* — increased report limits and prioritized processing by city services.

---

### 🏛️ For Administrators (Web / Backend)

- 🧩 **Admin Dashboard** — full access to all reports (active and completed) with advanced sorting and filtering.  
- 👤 **User Management** — view user profiles and block rule violators.  
- ⚙️ **Report Editing Tools** — edit, update, or delete reports as needed.  
- 📊 **Analytics & Statistics** — track user activity and service performance through real-time data.

---

### 🧰 For Municipal Services (Web)

- 🪪 **Assigned Reports View** — access all reports assigned to a specific organization.  
- 🔄 **Status Updates** — change report states (“Accepted”, “In Progress”, “Completed”, etc.).  
- 📷 **Photo Reports** — upload visual proof of completed work.  
- 💬 **Comment System** — communicate with users to clarify details or provide updates.

---

> 💡 These features form the core of **UpCity**, creating a transparent and efficient communication bridge between citizens and municipal authorities.


<a id="preview-user-flow"></a>
## 🖼️ Preview / User Flow

### 1️⃣ Registration & Login
<p align="center">
  <img src="https://i.postimg.cc/VkpBgcGG/login.png" width="300" alt="Login">
  <img src="https://i.postimg.cc/K8fh3J0k/registration.png" width="303" alt="Registrationn">
  
</p>
*Quick and secure registration/login for all users.*

---

### 2️⃣ Main Map / Reports Page
<p align="center">
  <img src="https://i.postimg.cc/BbPJxHjJ/main-map.png" width="292" alt="Main_map">
  <img src="https://i.postimg.cc/jdWDXnpJ/reports-page.png" width="300" alt="Reports">
  
</p>
*Interactive map showing all city reports.*

---

### 3️⃣ Create & View Report
<p align="center">
  <img src="https://i.postimg.cc/wTH6ty9S/crt-rep.png" width="300" alt="Create Report">
  <img src="https://i.postimg.cc/QxN2Gp8r/view-rep.png" width="300" alt="View Report">
  
</p>
*Users can create new reports and check their status.*

---

### 4️⃣ My Reports / All Reports
<p align="center">
  <img src="https://i.postimg.cc/3JyZvR9N/my-Rep.png" width="300" alt="My Reports">
  <img src="https://i.postimg.cc/pXnDdSXn/all-rep.png" width="295" alt="All Reports">
  
</p>
*Easily manage your own reports or browse all reports.*

<a id="demo-video"></a>
## 🎥 Demo Video

<p align="center">
  🎬 <a href="./demo/demo.mp4">Watch demo video for application</a>
  🎬 <a href="./demo/demo.mp4">Watch demo video for website</a>
  
</p>

---
<a id="project-architecture"></a>
## 🏗️ Project Architecture

The project is organized as follows:

UPCITY/
- 📁 AndroidApp      # Android mobile application
- 📁 Backend         # FastAPI server
- 📁 Web             # React web application
- 📁 docs            # Documentation (PDFs, diagrams)
README.md          # Project README



Each part of the system can be developed and run independently.
---


<a id="tech-stack"></a>
## 🛠️ Tech Stack

<p align="center">
  <img src="https://img.shields.io/badge/Frontend-React-61DAFB?style=for-the-badge&logo=react&logoColor=white" alt="React">
  <img src="https://img.shields.io/badge/Styling-TailwindCSS-38B2AC?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="TailwindCSS">
  <img src="https://img.shields.io/badge/HTTP-Axios-5A29E4?style=for-the-badge&logo=axios&logoColor=white" alt="Axios">
  <img src="https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Language-Python%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Database-PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Mobile-Java-007396?style=for-the-badge&logo=java&logoColor=white" alt="Java">
  <img src="https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white" alt="GitHub Actions">
  <img src="https://img.shields.io/badge/Auth-JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white" alt="JWT">
  <img src="https://img.shields.io/badge/Maps-Google%20Maps%20API-4285F4?style=for-the-badge&logo=googlemaps&logoColor=white" alt="Google Maps API">
</p>

**Frontend:** React, TailwindCSS, Axios  
**Backend:** FastAPI (Python 3.12)  
**Database:** PostgreSQL  
**Mobile:** Android (Java)  
**Other Tools:** GitHub Actions, JWT Auth, Google Maps API

---



<a id="documentation"></a>
## 📘 Documentation

All supporting materials are located in the [`docs/`](./docs) folder:

- [Vision and Scope](./docs/01_vision_and_scope.pdf)  
- [Business Rules](./docs/02_business_rules.pdf)  
- [Smart Use Case Diagram](./docs/03_smart_use_case_diagram.pdf)  
- [Class Diagram](./docs/04_class_diagram.pdf)  
- [Component Diagram](./docs/05_component_diagram.pdf)  
- [CRC Cards](./docs/06_crc_cards.pdf)  
- [Deployment Diagram](./docs/07_deployment_diagram.pdf)  
- [Mind Map](./docs/08_mind_map.pdf)  
- [Object Diagram](./docs/09_object_diagram.pdf)  
- [State Chart](./docs/10_state_chart.pdf)  


<a id="developers"></a>
## 👨‍💻 Developers

- [Serge Kozlov](https://github.com/kozlov4) - Backend Dev, Architect
- [Denys Kukulenko](https://github.com/NureKukulenkoDenys) - FrontendDev
- [Yelyzaveta Denysenko](https://github.com/Yelyzaveta-denysenko-vit) - UI/UX Designer
- [Anna But](https://github.com/annabut08) - Backend Dev, Database Architect
- [Kyrylo Kyrychenko](https://github.com/kerio1) - Backend Dev
- [Zakhar Koryakin](https://github.com/DreamYwY) - Mobile Dev

<a id="license"></a>
## 📜 License

MIT License

Copyright (c) 2025 UpCity Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

