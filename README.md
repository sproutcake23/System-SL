# ⚔️ SL — The SYSTEM

> _“Arise, Player.”_  
A CLI-based personal progression system inspired by **Solo Leveling**.  
The SYSTEM assigns tasks, reminds you through the day, and tracks your growth — right from your terminal.

---

## 🧭 Overview

**SL** is a lightweight Linux command-line program that helps you build consistent habits and level up in real life.
No browser, no accounts — just a self-hosted assistant that lives on your machine, keeps track of your goals, and motivates you to complete them.

---

## 🚀 Features

- 📝 Add, list, and complete tasks from the terminal  
- 🔔 Desktop notifications (Debian / Fedora / Arch compatible)  
- ⏰ Background reminder loop for incomplete tasks  
- 🧠 XP and Level system for motivation  
- 💾 Local JSON storage — no cloud, no tracking  

---

## 📦 Setup

### Requirements

- Linux (Debian, Fedora, Arch, or similar)  
- Python ≥ 3.10  
- `notify-send` (usually included by default)

### Installation

```bash
git clone <https://github.com/sproutcake23/System-SL.git>
cd SL
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
