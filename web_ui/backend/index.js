// import React from 'react';
// import ReactDOM from 'react-dom';
// import AppRouter from './Router';

// // Frontend rendering
// ReactDOM.render(
//     ReactDOM.render(
//         <AppRouter />,
//         document.getElementById('root')
//     )
// );

// To connect with your mongoDB database
const mongoose = require('mongoose');
mongoose.connect('mongodb+srv://charlenechenn:Atlas22331144!@cluster0.jbsx2.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0', {
    dbName: 'Cluster0',
    useNewUrlParser: true,
    useUnifiedTopology: true
})
.then(() => console.log("Connected to MongoDB successfully"))
.catch(err => console.error("MongoDB connection error:", err));

// Schema for users of app
const UserSchema = new mongoose.Schema({
    name: {
        type: String,
        required: true,
    },
    password: {
        type: String,
        required: true,
    },
    number: {
        type: Number,
        required: true,
        unique: true,
    },
    language: {
        type: String,
        default: "English",
        required: true,
    }
});
const User = mongoose.model('users', UserSchema);
User.createIndexes();

// For backend and express
const express = require('express');
const app = express();
const cors = require("cors");
console.log("App listen at port 5001");
app.use(express.json());
app.use(cors());
app.get("/", (req, resp) => {

    resp.send("App is Working");
    // You can check backend is working or not by 
    // entering http://localhost:5001
    
    // If you see App is working means
    // backend working properly
});

app.post("/register", async (req, resp) => {
    try {
        const user = new User(req.body);
        let result = await user.save();
        result = result.toObject();
        if (result) {
            delete result.password;
            resp.send(req.body);
            console.log(result);
        } else {
            console.log("User already register");
        }
    } catch (e) {
        resp.status(500).send("Something Went Wrong");
    }
});

app.post("/login", async (req, resp) => {
    try {
        const user = await User.findOne({ name: req.body.name, password: req.body.password });
        if (user) {
            resp.send(user);
        } else {
            resp.send("Invalid credentials");
        }
    } catch (e) {
        resp.status(500).send("Something Went Wrong");
    }
});
app.listen(5001);