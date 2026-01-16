<template>
    <aside class="sidebar">
        <!-- Popular Posts Widget -->
        <SidebarPopularPosts v-if="showPopular" />

        <!-- Categories Widget -->
        <SidebarCategories v-if="showCategories" />

        <!-- Subscription Widget -->
        <SidebarSubscription v-if="showSubscription" />

        <!-- Custom slot for additional content -->
        <slot />
    </aside>
</template>

<script setup lang="ts">
import SidebarPopularPosts from '@/components/layout/SidebarPopularPosts.vue'
import SidebarCategories from '@/components/layout/SidebarCategories.vue'
import SidebarSubscription from '@/components/layout/SidebarSubscription.vue'

interface Props {
    showPopular?: boolean
    showCategories?: boolean
    showSubscription?: boolean
}

withDefaults(defineProps<Props>(), {
    showPopular: true,
    showCategories: true,
    showSubscription: true,
})
</script>

<style scoped>
.sidebar {
    position: sticky;
    top: 2rem;
    height: fit-content;
}

@media (max-width: 1024px) {
    .sidebar {
        position: relative;
        top: 0;
    }
}
</style>
