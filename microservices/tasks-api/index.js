const express = require("express");
const app = express();
app.use(express.json());

// In-memory store — you'll replace with a real DB later
const tasks = [
  { id: 1, title: "Learn Docker", done: false },
  { id: 2, title: "Learn GitHub Actions", done: false },
  { id: 3, title: "Learn Terraform", done: false },
  { id: 4, title: "Learn Kubernetes", done: false },
  { id: 5, title: "Learn Microservices", done: false },
  { id: 6, title: "Deploy to the Cloud", done: false },
];

app.get("/health", (req, res) => {
  res.json({ status: "ok", service: "tasks-api" });
});

app.get("/tasks", (req, res) => {
  res.json({ tasks });
});

app.post("/tasks", (req, res) => {
  const { title } = req.body;
  if (!title || typeof title !== "string") {
    return res.status(400).json({ error: "title is required" });
  }
  const task = { id: tasks.length + 1, title, done: false };
  tasks.push(task);
  res.status(201).json({ task });
});

const PORT = process.env.PORT ?? 4000;
app.listen(PORT, () => {
  console.log(`tasks-api running on port ${PORT}`);
});
