<template>
  <div class="min-h-screen bg-dark-950">
    <!-- Hero Section -->
    <section class="bg-gradient-to-br from-primary-600 to-primary-500 py-20">
      <div class="container-content text-center">
        <h1 class="text-5xl font-bold text-white mb-4">About TechNews</h1>
        <p class="text-xl text-primary-100 max-w-2xl mx-auto">
          Your premier destination for technology news, insights, and community discussions
        </p>
      </div>
    </section>

    <!-- Mission Section -->
    <section class="py-16">
      <div class="container-narrow">
        <div class="card">
          <div class="card-body">
            <h2 class="text-3xl font-bold text-dark-100 mb-6 text-center">Our Mission</h2>
            <p class="text-lg text-dark-300 mb-4">
              TechNews is dedicated to providing a platform where technology enthusiasts, developers, and innovators
              can share their knowledge, insights, and experiences with a global community.
            </p>
            <p class="text-lg text-dark-300">
              We believe in the power of shared knowledge and open discussion to drive innovation and help everyone
              stay informed about the rapidly evolving world of technology.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-16 bg-dark-800">
      <div class="container-content">
        <h2 class="text-3xl font-bold text-dark-100 mb-12 text-center">What We Offer</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="card hover:border-primary-500 transition-colors">
            <div class="card-body text-center">
              <div class="w-16 h-16 bg-primary-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg class="w-8 h-8 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <h3 class="text-xl font-semibold text-dark-100 mb-3">Quality Content</h3>
              <p class="text-dark-400">
                Curated articles and posts from experienced developers and tech enthusiasts covering the latest trends
                and best practices.
              </p>
            </div>
          </div>

          <div class="card hover:border-primary-500 transition-colors">
            <div class="card-body text-center">
              <div class="w-16 h-16 bg-primary-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg class="w-8 h-8 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h3 class="text-xl font-semibold text-dark-100 mb-3">Active Community</h3>
              <p class="text-dark-400">
                Engage with like-minded individuals, share your thoughts, and participate in meaningful discussions
                about technology.
              </p>
            </div>
          </div>

          <div class="card hover:border-primary-500 transition-colors">
            <div class="card-body text-center">
              <div class="w-16 h-16 bg-primary-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg class="w-8 h-8 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 class="text-xl font-semibold text-dark-100 mb-3">Stay Updated</h3>
              <p class="text-dark-400">
                Get the latest news, tutorials, and insights delivered to you. Never miss important updates in the
                tech world.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Values Section -->
    <section class="py-16">
      <div class="container-narrow">
        <h2 class="text-3xl font-bold text-dark-100 mb-12 text-center">Our Values</h2>
        <div class="space-y-6">
          <div class="card">
            <div class="card-body">
              <h3 class="text-xl font-semibold text-dark-100 mb-2">🎯 Quality First</h3>
              <p class="text-dark-300">
                We prioritize high-quality, well-researched content that provides real value to our readers.
              </p>
            </div>
          </div>

          <div class="card">
            <div class="card-body">
              <h3 class="text-xl font-semibold text-dark-100 mb-2">🤝 Community Driven</h3>
              <p class="text-dark-300">
                Our platform is built by the community, for the community. Every voice matters and contributes to our
                collective knowledge.
              </p>
            </div>
          </div>

          <div class="card">
            <div class="card-body">
              <h3 class="text-xl font-semibold text-dark-100 mb-2">🚀 Innovation</h3>
              <p class="text-dark-300">
                We embrace new technologies and continuously improve our platform to provide the best user experience.
              </p>
            </div>
          </div>

          <div class="card">
            <div class="card-body">
              <h3 class="text-xl font-semibold text-dark-100 mb-2">🌐 Accessibility</h3>
              <p class="text-dark-300">
                We believe technology knowledge should be accessible to everyone, regardless of their background or
                experience level.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="py-16 bg-dark-800">
      <div class="container-content text-center">
        <h2 class="text-3xl font-bold text-dark-100 mb-4">Join Our Community</h2>
        <p class="text-lg text-dark-300 mb-8 max-w-2xl mx-auto">
          Start sharing your knowledge, learn from others, and be part of a growing community of tech enthusiasts.
        </p>
        <div class="flex justify-center space-x-4">
          <router-link to="/register" class="btn btn-primary btn-lg">
            Get Started
          </router-link>
          <router-link to="/posts" class="btn btn-outline btn-lg">
            Browse Posts
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
// Static about page - no logic needed
</script>
