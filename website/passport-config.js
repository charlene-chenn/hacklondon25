const LocalStrategy = require("passport-local").Strategy
const bcrypt = require("bcrypt")
const User = require("./models/user")

function initialize(passport) {
  const authenticateUsers = async (email, password, done) => {
    try {
      const user = await User.findOne({ email: email })
      if (!user) {
        return done(null, false, { message: "No user found with that email" })
      }
      if (await bcrypt.compare(password, user.password)) {
        return done(null, user)
      } else {
        return done(null, false, { message: "Password Incorrect" })
      }
    } catch (e) {
      return done(e)
    }
  }

  passport.use(new LocalStrategy({ usernameField: "email" }, authenticateUsers))
  passport.serializeUser((user, done) => done(null, user.id))
  passport.deserializeUser(async (id, done) => {
    try {
      const user = await User.findById(id)
      return done(null, user)
    } catch (e) {
      return done(e)
    }
  })
}


module.exports = initialize