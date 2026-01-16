<template>
    <div class="subscription-box">
        <h3>Subscribe Today</h3>
        <p>Get unlimited access to premium content</p>

        <div v-if="loading" class="text-center py-4">
            <div class="loading-spinner"></div>
        </div>

        <div v-else-if="plans.length > 0" class="pricing-mini">
            <div v-for="(plan, index) in plans.slice(0, 3)" :key="plan.id" class="price-option"
                :class="{ 'featured': index === 1 }">
                <div class="price-name">{{ plan.name }}</div>
                <div class="price-amount">
                    ${{ parseFloat(plan.price).toFixed(0) }}
                    <span>/{{ plan.duration_days }}d</span>
                </div>
            </div>
        </div>

        <router-link to="/subscriptions" class="subscribe-btn-sidebar">
            View All Plans
        </router-link>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useSubscriptionsStore } from '@/stores/subscriptions'

const subscriptionsStore = useSubscriptionsStore()
const loading = ref(false)

const plans = computed(() => subscriptionsStore.plans || [])

onMounted(async () => {
    if (plans.value.length === 0) {
        loading.value = true
        try {
            await subscriptionsStore.fetchPlans()
        } catch (error) {
            console.error('Failed to load plans:', error)
        } finally {
            loading.value = false
        }
    }
})
</script>

<style scoped>
.subscription-box {
    background: linear-gradient(135deg, #16213e, #1a1a2e);
    color: white;
    padding: 2rem;
    text-align: center;
    border-radius: 0;
    margin-bottom: 2rem;
}

.subscription-box h3 {
    font-family: 'Merriweather', serif;
    font-size: 1.5rem;
    margin-bottom: 1rem;
}

.subscription-box p {
    margin-bottom: 1.5rem;
    opacity: 0.9;
    color: #C8C3BC;
}

.pricing-mini {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.price-option {
    background: #181A1B;
    padding: 1rem;
    border-radius: 0;
    border: 1px solid rgba(255, 255, 255, 0);
    transition: all 0.3s;
}

.price-option:hover {
    background: rgba(255, 255, 255, 0.15);
}

.price-option.featured {
    background: #9D1329;
    border-color: #9D1329;
}

.price-name {
    font-weight: 700;
    margin-bottom: 0.5rem;
    color: #E8E6E3;
}

.price-amount {
    font-size: 1.75rem;
    font-weight: 700;
    color: #E8E6E3;
}

.price-amount span {
    font-size: 0.875rem;
    color: #A8A095;
}

.subscribe-btn-sidebar {
    display: inline-block;
    background: #9D1329;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 0;
    text-decoration: none;
    font-weight: 700;
    transition: background 0.3s;
}

.subscribe-btn-sidebar:hover {
    background: #d63653;
}
</style>
