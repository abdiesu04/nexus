'use client'

import React, { useEffect, useRef } from 'react'
import { motion, useScroll, useTransform, useSpring } from 'framer-motion'
import Link from 'next/link'
import HeroAnimation from './components/HeroAnimation'
import { 
  UserGroupIcon, 
  ClockIcon, 
  DevicePhoneMobileIcon, 
  ShieldCheckIcon,
  UserIcon,
  ChatBubbleLeftRightIcon,
  DocumentCheckIcon,
  HeartIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'

const FloatingParticle = ({ delay = 0 }) => {
  return (
    <motion.div
      className="absolute w-2 h-2 bg-blue-500/20 rounded-full"
      animate={{
        y: [-20, 20],
        opacity: [0.2, 0.5, 0.2],
        scale: [1, 1.5, 1],
      }}
      transition={{
        duration: 3,
        repeat: Infinity,
        delay,
      }}
    />
  )
}

export default function Home() {
  const targetRef = useRef(null)
  const { scrollYProgress } = useScroll({
    target: targetRef,
    offset: ["start start", "end start"]
  })

  const springScrollY = useSpring(scrollYProgress, {
    stiffness: 100,
    damping: 30,
    restDelta: 0.001
  })

  const heroScale = useTransform(springScrollY, [0, 1], [1, 0.8])
  const heroOpacity = useTransform(springScrollY, [0, 0.5], [1, 0])

  return (
    <main className="min-h-screen" ref={targetRef}>
      {/* Hero Section */}
      <section className="relative min-h-screen pt-16 flex items-center bg-gradient-to-br from-white to-blue-50 overflow-hidden">
        {/* Floating particles */}
        <div className="absolute inset-0 pointer-events-none">
          {[...Array(20)].map((_, i) => (
            <FloatingParticle key={i} delay={i * 0.2} />
          ))}
        </div>

        {/* Gradient orbs */}
        <div className="absolute top-20 right-20 w-72 h-72 bg-blue-400/20 rounded-full filter blur-3xl animate-pulse" />
        <div className="absolute bottom-20 left-20 w-96 h-96 bg-purple-400/20 rounded-full filter blur-3xl animate-pulse" />

        <motion.div 
          className="container mx-auto px-4 sm:px-6 lg:px-8 relative"
          style={{ scale: heroScale, opacity: heroOpacity }}
        >
          <div className="relative z-10 lg:w-1/2 py-12">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="space-y-8"
            >
              <div className="relative">
                <motion.div
                  className="absolute -top-6 -left-6 w-12 h-12 text-blue-600"
                  animate={{
                    rotate: 360,
                    scale: [1, 1.2, 1],
                  }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                    ease: "linear"
                  }}
                >
                  <SparklesIcon />
                </motion.div>
                <motion.h1 
                  className="text-5xl md:text-7xl font-bold leading-tight"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.8, delay: 0.2 }}
                >
                  Smart Care,{' '}
                  <motion.span
                    className="bg-gradient-to-r from-blue-600 via-blue-700 to-blue-800 bg-clip-text text-transparent inline-block"
                    initial={{ opacity: 0, scale: 0.5 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ 
                      delay: 0.5, 
                      duration: 0.8,
                      type: "spring",
                      stiffness: 100
                    }}
                  >
                    Anywhere
                  </motion.span>
                </motion.h1>
              </div>
              <motion.p 
                className="text-xl md:text-2xl text-gray-600 max-w-xl leading-relaxed"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.4 }}
              >
                Expert doctors at your fingertips. Quality healthcare, when you need it.
              </motion.p>
              <motion.div 
                className="flex flex-col sm:flex-row gap-4"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.6 }}
              >
                <Link href="/register">
                  <motion.button
                    className="btn-primary px-8 py-4 rounded-full text-lg font-semibold w-full sm:w-auto relative overflow-hidden group"
                    whileHover={{ 
                      scale: 1.05,
                      boxShadow: "0 10px 30px -10px rgba(59, 130, 246, 0.5)"
                    }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <motion.span
                      className="absolute inset-0 bg-white/20"
                      initial={{ x: "-100%" }}
                      whileHover={{ x: "100%" }}
                      transition={{ duration: 0.5 }}
                    />
                    Start Your Journey
                  </motion.button>
                </Link>
                <Link href="/about">
                  <motion.button
                    className="btn-secondary px-8 py-4 rounded-full text-lg font-semibold w-full sm:w-auto relative overflow-hidden group"
                    whileHover={{ 
                      scale: 1.05,
                      boxShadow: "0 10px 30px -10px rgba(59, 130, 246, 0.3)"
                    }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <motion.span
                      className="absolute inset-0 bg-blue-50"
                      initial={{ x: "-100%" }}
                      whileHover={{ x: "100%" }}
                      transition={{ duration: 0.5 }}
                    />
                    Discover More
                  </motion.button>
                </Link>
              </motion.div>
            </motion.div>
          </div>
        </motion.div>
        <HeroAnimation />
      </section>

      {/* Features Section with enhanced animations */}
      <section className="py-20 bg-white relative">
        <div className="absolute inset-0 bg-gradient-to-b from-blue-50/50 to-transparent" />
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <motion.div
              className="inline-block"
              whileHover={{ scale: 1.05 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
                Why Choose Hakime?
              </h2>
            </motion.div>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Experience healthcare that puts you first with our comprehensive suite of services
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              { icon: ClockIcon, title: '24/7 Support', desc: 'Round-the-clock medical assistance whenever you need it' },
              { icon: UserGroupIcon, title: 'Expert Doctors', desc: 'Access to qualified healthcare professionals' },
              { icon: DevicePhoneMobileIcon, title: 'Modern Tech', desc: 'State-of-the-art telemedicine platform' },
              { icon: ShieldCheckIcon, title: 'Secure & Private', desc: 'Your health data is protected with top-tier security' }
            ].map((feature, index) => (
              <motion.div
                key={feature.title}
                className="feature-card group"
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ 
                  opacity: 1, 
                  y: 0,
                  transition: {
                    type: "spring",
                    bounce: 0.4,
                    duration: 1,
                    delay: index * 0.2
                  }
                }}
                viewport={{ once: true, margin: "-100px" }}
                whileHover={{ 
                  scale: 1.05,
                  boxShadow: "0 20px 40px -20px rgba(59, 130, 246, 0.3)",
                  y: -5
                }}
              >
                <div className="relative">
                  <motion.div
                    className="absolute inset-0 bg-blue-100 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                    animate={{
                      scale: [1, 1.2, 1],
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                    }}
                  />
                  <motion.div
                    initial={{ scale: 0 }}
                    whileInView={{ 
                      scale: 1,
                      transition: {
                        type: "spring",
                        stiffness: 200,
                        delay: index * 0.2 + 0.3
                      }
                    }}
                    viewport={{ once: true }}
                    className="relative z-10"
                  >
                    <feature.icon className="w-12 h-12 text-blue-600 mb-4 transform group-hover:rotate-12 transition-transform duration-300" />
                  </motion.div>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors duration-300">
                  {feature.title}
                </h3>
                <p className="text-gray-600 group-hover:text-gray-900 transition-colors duration-300">
                  {feature.desc}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">How It Works</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Get started with Hakime in three simple steps
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { icon: UserIcon, title: 'Create Account', desc: 'Sign up and complete your health profile' },
              { icon: ChatBubbleLeftRightIcon, title: 'Book Consultation', desc: 'Choose your doctor and schedule a visit' },
              { icon: HeartIcon, title: 'Get Care', desc: 'Receive personalized care and treatment' }
            ].map((step, index) => (
              <motion.div
                key={step.title}
                className="text-center"
                initial={{ opacity: 0, x: index % 2 === 0 ? -50 : 50 }}
                whileInView={{ 
                  opacity: 1, 
                  x: 0,
                  transition: {
                    type: "spring",
                    bounce: 0.4,
                    duration: 1,
                    delay: index * 0.2
                  }
                }}
                viewport={{ once: true, margin: "-100px" }}
              >
                <div className="relative mb-8">
                  <motion.div 
                    className="w-20 h-20 mx-auto bg-blue-100 rounded-full flex items-center justify-center"
                    whileHover={{ 
                      scale: 1.1,
                      rotate: 360,
                      transition: { duration: 0.5 }
                    }}
                  >
                    <step.icon className="w-10 h-10 text-blue-600" />
                  </motion.div>
                  {index < 2 && (
                    <motion.div 
                      className="hidden md:block absolute top-10 left-[60%] w-full h-0.5 bg-blue-100"
                      initial={{ scaleX: 0 }}
                      whileInView={{ 
                        scaleX: 1,
                        transition: {
                          duration: 1,
                          delay: 0.5
                        }
                      }}
                      viewport={{ once: true }}
                    />
                  )}
                </div>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ 
                    opacity: 1, 
                    y: 0,
                    transition: {
                      duration: 0.5,
                      delay: index * 0.2 + 0.5
                    }
                  }}
                  viewport={{ once: true }}
                >
                  <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                  <p className="text-gray-600">{step.desc}</p>
                </motion.div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-blue-800 text-white">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Ready to Get Started?</h2>
            <p className="text-xl mb-8 opacity-90">
              Join thousands of patients who trust Hakime for their healthcare needs
            </p>
            <Link href="/register">
              <motion.button
                className="bg-white text-blue-600 px-8 py-4 rounded-full text-lg font-semibold"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Sign Up Now
              </motion.button>
            </Link>
          </motion.div>
        </div>
      </section>
    </main>
  )
}
