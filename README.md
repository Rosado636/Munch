Munch & Tell
🍔 Munch & Tell is a food blog application with a backend API built in FastAPI and PostgreSQL, designed to review and promote local restaurants.

🚀 Features
Full CRUD for restaurants:

Create, read, update, delete

Fields: name, description, location, rating, image, category, website

Reviews for restaurants:

Add, list, update, soft-delete reviews

Soft delete with allowed reasons (spam, offensive, admin_request, others)

Audit-friendly: reviews hidden instead of deleted permanently

API documentation via Swagger UI (/docs)

🛠️ Tech Stack
Python 3.11+

FastAPI

SQLModel (ORM)

PostgreSQL

Uvicorn (ASGI server)

⚡ Local development setup
1️⃣ Clone the repo:

git clone https://github.com/Rosado636/Munch.git
cd Munch/backE
2️⃣ Install dependencies:

pip install -r requirements.txt
3️⃣ Set up environment variables:

Create a .env file with your PostgreSQL database connection string:

DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/munchdb
4️⃣ Run the server:

uvicorn app.main:app --reload
✅ Swagger UI available at:

http://localhost:8000/docs
🔒 Security considerations
.env is excluded from version control via .gitignore

Soft delete strategy used for sensitive review management

Future enhancements planned: authentication, user roles, pagination

🛆 Future work
User accounts + authentication

Admin panel for moderation

Frontend integration (Next.js)

Dockerization for deployment

🧑‍💻 Author
Anthony Rosado

GitHub: @Rosado636

📄 License
This project is open source and available under the MIT License.
