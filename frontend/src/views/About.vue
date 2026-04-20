<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Hero Section -->
    <div class="bg-gradient-to-br from-gray-800 to-gray-900 text-white py-12 md:py-20">
      <div class="max-w-7xl mx-auto px-4 md:px-6 text-center">
        <h1 class="text-2xl md:text-4xl font-bold mb-3 md:mb-4">Membership Plans</h1>
        <p class="text-base md:text-lg opacity-90 max-w-3xl mx-auto px-4">Unlock premium features and start trading with confidence</p>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 md:px-6 py-8 md:py-12 space-y-12 md:space-y-16">
      <!-- Membership Plans -->
      <section>
        <div class="text-center mb-8 md:mb-12">
          <h2 class="text-xl md:text-3xl font-bold text-gray-900 mb-3 md:mb-4">Choose Your Plan</h2>
          <p class="text-sm md:text-base text-gray-600">All prices in USDT - No hidden fees</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6 lg:gap-8">
          <!-- Monthly Plan -->
          <div class="bg-white rounded-xl shadow-lg overflow-hidden border-2 border-gray-200 hover:border-gray-400 transition-all hover:shadow-xl">
            <div class="p-5 md:p-8">
              <div class="text-center mb-5 md:mb-6">
                <div class="w-16 h-16 md:w-20 md:h-20 mx-auto mb-3 md:mb-4 bg-gradient-to-br from-gray-600 to-gray-800 rounded-full flex items-center justify-center">
                  <i class="fa-solid fa-crown text-2xl md:text-3xl text-white"></i>
                </div>
                <h3 class="text-lg md:text-xl font-bold text-gray-900 mb-2">Monthly</h3>
                <div class="flex items-baseline justify-center">
                  <span class="text-3xl md:text-4xl font-bold text-gray-900">1</span>
                  <span class="text-base md:text-lg text-gray-600 ml-2">USDT</span>
                </div>
                <p class="text-xs md:text-sm text-gray-500 mt-1">per month</p>
              </div>

              <ul class="space-y-3 mb-8">
                <li class="flex items-start">
                  <i class="fa-solid fa-check-circle text-green-500 mt-1 mr-3"></i>
                  <span class="text-sm text-gray-700">Unlimited product trials</span>
                </li>
                <li class="flex items-start">
                  <i class="fa-solid fa-check-circle text-green-500 mt-1 mr-3"></i>
                  <span class="text-sm text-gray-700">Access all platform products</span>
                </li>
                <li class="flex items-start">
                  <i class="fa-solid fa-check-circle text-green-500 mt-1 mr-3"></i>
                  <span class="text-sm text-gray-700">Escrow service protection</span>
                </li>
                <li class="flex items-start">
                  <i class="fa-solid fa-check-circle text-green-500 mt-1 mr-3"></i>
                  <span class="text-sm text-gray-700">24/7 customer support</span>
                </li>
              </ul>

              <button class="w-full py-2.5 md:py-3 border-2 border-gray-700 text-gray-700 rounded-lg font-medium hover:bg-gray-100 transition-colors text-sm md:text-base">
                Choose Plan
              </button>
            </div>
          </div>

          <!-- Yearly Plan (Popular) -->
          <div class="bg-white rounded-xl shadow-2xl overflow-hidden border-2 border-gray-700 relative transform md:-translate-y-2 lg:-translate-y-4">
            <div class="absolute top-0 right-0 bg-gray-900 text-white px-3 md:px-4 py-1 text-xs font-bold rounded-bl-lg">
              POPULAR
            </div>
            <div class="p-5 md:p-8">
              <div class="text-center mb-5 md:mb-6">
                <div class="w-16 h-16 md:w-20 md:h-20 mx-auto mb-3 md:mb-4 bg-gradient-to-br from-gray-700 to-gray-900 rounded-full flex items-center justify-center">
                  <i class="fa-solid fa-gem text-2xl md:text-3xl text-white"></i>
                </div>
                <h3 class="text-lg md:text-xl font-bold text-gray-900 mb-2">Yearly</h3>
                <div class="flex items-baseline justify-center">
                  <span class="text-3xl md:text-4xl font-bold text-gray-900">5</span>
                  <span class="text-base md:text-lg text-gray-600 ml-2">USDT</span>
                </div>
                <p class="text-xs md:text-sm text-gray-500 mt-1">per year</p>
                <p class="text-xs text-green-600 mt-2 font-semibold">Save 58%</p>
              </div>

              <ul class="space-y-3 mb-8">
                <li class="flex items-start">
                  <i class="fa-solid fa-check-circle text-green-500 mt-1 mr-3"></i>
                  <span class="text-sm text-gray-700">Unlimited product trials</span>
                </li>
                <li class="flex items-start">
                  <i class="fa-solid fa-check-circle text-green-500 mt-1 mr-3"></i>
                  <span class="text-sm text-gray-700">Access all platform products</span>
                </li>
                <li class="flex items-start">
                  <i class="fa-solid fa-check-circle text-green-500 mt-1 mr-3"></i>
                  <span class="text-sm text-gray-700">Escrow service protection</span>
                </li>
                <li class="flex items-start">
                  <i class="fa-solid fa-check-circle text-green-500 mt-1 mr-3"></i>
                  <span class="text-sm text-gray-700">Priority customer support</span>
                </li>
                <li class="flex items-start">
                  <i class="fa-solid fa-check-circle text-green-500 mt-1 mr-3"></i>
                  <span class="text-sm text-gray-700">Exclusive discounts</span>
                </li>
              </ul>

              <button class="w-full py-2.5 md:py-3 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-800 transition-all shadow-lg text-sm md:text-base">
                Choose Plan
              </button>
            </div>
          </div>

          <!-- Lifetime Plan -->
          <div class="bg-white rounded-xl shadow-lg overflow-hidden border-2 border-gray-200 hover:border-gray-400 transition-all hover:shadow-xl">
            <div class="p-5 md:p-8">
              <div class="text-center mb-5 md:mb-6">
                <div class="w-16 h-16 md:w-20 md:h-20 mx-auto mb-3 md:mb-4 bg-gradient-to-br from-gray-700 to-gray-900 rounded-full flex items-center justify-center">
                  <i class="fa-solid fa-infinity text-2xl md:text-3xl text-white"></i>
                </div>
                <h3 class="text-lg md:text-xl font-bold text-gray-900 mb-2">Lifetime</h3>
                <div class="flex items-baseline justify-center">
                  <span class="text-3xl md:text-4xl font-bold text-gray-900">10</span>
                  <span class="text-base md:text-lg text-gray-600 ml-2">USDT</span>
                </div>
                <p class="text-xs md:text-sm text-gray-500 mt-1">one-time payment</p>
                <p class="text-xs text-gray-600 mt-2 font-semibold">Best Value</p>
              </div>

              <ul class="space-y-3 mb-8">
                <li class="flex items-start">
                  <i class="fa-solid fa-check-circle text-green-500 mt-1 mr-3"></i>
                  <span class="text-sm text-gray-700">Unlimited product trials</span>
                </li>
                <li class="flex items-start">
                  <i class="fa-solid fa-check-circle text-green-500 mt-1 mr-3"></i>
                  <span class="text-sm text-gray-700">Access all platform products</span>
                </li>
                <li class="flex items-start">
                  <i class="fa-solid fa-check-circle text-green-500 mt-1 mr-3"></i>
                  <span class="text-sm text-gray-700">Escrow service protection</span>
                </li>
                <li class="flex items-start">
                  <i class="fa-solid fa-check-circle text-green-500 mt-1 mr-3"></i>
                  <span class="text-sm text-gray-700">Priority customer support</span>
                </li>
                <li class="flex items-start">
                  <i class="fa-solid fa-check-circle text-green-500 mt-1 mr-3"></i>
                  <span class="text-sm text-gray-700">VIP exclusive benefits</span>
                </li>
                <li class="flex items-start">
                  <i class="fa-solid fa-check-circle text-green-500 mt-1 mr-3"></i>
                  <span class="text-sm text-gray-700">Lifetime access & updates</span>
                </li>
              </ul>

              <button class="w-full py-2.5 md:py-3 border-2 border-gray-700 text-gray-700 rounded-lg font-medium hover:bg-gray-100 transition-colors text-sm md:text-base">
                Choose Plan
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- VIP Benefits -->
      <section class="bg-white rounded-xl shadow-sm p-5 md:p-8">
        <h2 class="text-xl md:text-3xl font-bold text-gray-900 mb-6 md:mb-8 text-center">Membership Benefits</h2>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
          <div class="p-6 border border-gray-200 rounded-lg hover:border-blue-500 transition-colors">
            <i class="fa-solid fa-comments text-3xl text-blue-600 mb-4"></i>
            <h3 class="font-bold text-gray-900 mb-2">AI Consultation</h3>
            <p class="text-sm text-gray-600">Get instant answers from seller's AI assistant about products and services</p>
          </div>

          <div class="p-6 border border-gray-200 rounded-lg hover:border-purple-500 transition-colors">
            <i class="fa-solid fa-robot text-3xl text-purple-600 mb-4"></i>
            <h3 class="font-bold text-gray-900 mb-2">Smart Matching</h3>
            <p class="text-sm text-gray-600">AI helps match your requirements with the right developers</p>
          </div>

          <div class="p-6 border border-gray-200 rounded-lg hover:border-green-500 transition-colors">
            <i class="fa-solid fa-headset text-3xl text-green-600 mb-4"></i>
            <h3 class="font-bold text-gray-900 mb-2">Priority Support</h3>
            <p class="text-sm text-gray-600">Access to dedicated customer support team for assistance</p>
          </div>

          <div class="p-6 border border-gray-200 rounded-lg hover:border-orange-500 transition-colors">
            <i class="fa-solid fa-search text-3xl text-orange-600 mb-4"></i>
            <h3 class="font-bold text-gray-900 mb-2">Unlimited Browsing</h3>
            <p class="text-sm text-gray-600">Browse all products and contact sellers without restrictions</p>
          </div>

          <div class="p-6 border border-gray-200 rounded-lg hover:border-pink-500 transition-colors">
            <i class="fa-solid fa-lightbulb text-3xl text-pink-600 mb-4"></i>
            <h3 class="font-bold text-gray-900 mb-2">Requirement Posting</h3>
            <p class="text-sm text-gray-600">Post your project needs and receive proposals from developers</p>
          </div>

          <div class="p-6 border border-gray-200 rounded-lg hover:border-indigo-500 transition-colors">
            <i class="fa-solid fa-shield-alt text-3xl text-indigo-600 mb-4"></i>
            <h3 class="font-bold text-gray-900 mb-2">Optional Escrow</h3>
            <p class="text-sm text-gray-600">Choose platform escrow service for secure transactions (additional fee)</p>
          </div>
        </div>
      </section>

      <!-- Escrow Service -->
      <section class="bg-gray-100 rounded-xl p-5 md:p-8">
        <h2 class="text-xl md:text-3xl font-bold text-gray-900 mb-6 md:mb-8 text-center">Secure Escrow Service</h2>
        
        <div class="max-w-4xl mx-auto">
          <p class="text-center text-gray-600 mb-6 md:mb-8 text-sm md:text-base px-4">
            Our platform provides secure escrow services for custom development projects. 
            We hold payments safely until both buyer and seller are satisfied.
          </p>

          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
            <div class="text-center">
              <div class="w-12 h-12 md:w-16 md:h-16 mx-auto mb-3 md:mb-4 bg-white rounded-full flex items-center justify-center shadow-md">
                <span class="text-xl md:text-2xl font-bold text-gray-900">1</span>
              </div>
              <h3 class="font-semibold text-gray-900 mb-2 text-sm md:text-base">Agreement</h3>
              <p class="text-xs md:text-sm text-gray-600 px-2">Buyer and seller agree on project terms and deposit amount</p>
            </div>

            <div class="text-center">
              <div class="w-12 h-12 md:w-16 md:h-16 mx-auto mb-3 md:mb-4 bg-white rounded-full flex items-center justify-center shadow-md">
                <span class="text-xl md:text-2xl font-bold text-gray-900">2</span>
              </div>
              <h3 class="font-semibold text-gray-900 mb-2 text-sm md:text-base">Deposit</h3>
              <p class="text-xs md:text-sm text-gray-600 px-2">Seller submits order, buyer pays deposit to platform escrow</p>
            </div>

            <div class="text-center">
              <div class="w-12 h-12 md:w-16 md:h-16 mx-auto mb-3 md:mb-4 bg-white rounded-full flex items-center justify-center shadow-md">
                <span class="text-xl md:text-2xl font-bold text-gray-900">3</span>
              </div>
              <h3 class="font-semibold text-gray-900 mb-2 text-sm md:text-base">Development</h3>
              <p class="text-xs md:text-sm text-gray-600 px-2">Seller completes the work according to agreed specifications</p>
            </div>

            <div class="text-center">
              <div class="w-12 h-12 md:w-16 md:h-16 mx-auto mb-3 md:mb-4 bg-white rounded-full flex items-center justify-center shadow-md">
                <span class="text-xl md:text-2xl font-bold text-gray-900">4</span>
              </div>
              <h3 class="font-semibold text-gray-900 mb-2 text-sm md:text-base">Release</h3>
              <p class="text-xs md:text-sm text-gray-600 px-2">Both parties confirm acceptance, platform releases payment</p>
            </div>
          </div>

          <div class="mt-8 p-4 bg-white rounded-lg border-l-4 border-green-500">
            <div class="flex items-start">
              <i class="fa-solid fa-shield-alt text-green-500 text-xl mr-3 mt-1"></i>
              <div>
                <h4 class="font-semibold text-gray-900 mb-1">Why Use Escrow?</h4>
                <ul class="text-sm text-gray-600 space-y-1">
                  <li>�?Platform holds funds securely until project completion</li>
                  <li>�?Both buyer and seller are protected</li>
                  <li>�?Dispute resolution support if needed</li>
                  <li>�?Transparent transaction process</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA -->
      <section class="text-center px-4">
        <h2 class="text-xl md:text-3xl font-bold text-gray-900 mb-3 md:mb-4">Ready to Get Started?</h2>
        <p class="text-sm md:text-base text-gray-600 mb-6 md:mb-8">Join thousands of satisfied members today</p>
        <router-link to="/shop" class="inline-block px-6 md:px-8 py-3 md:py-4 bg-gray-900 text-white rounded-lg font-semibold hover:bg-gray-800 transition-all shadow-lg hover:shadow-xl text-sm md:text-base">
          Browse Products
        </router-link>
      </section>
    </div>
  </div>
</template>

<script setup>
// No need to import Navbar here, it's in Layout component
</script>
