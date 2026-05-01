<template>
  <div class="dashboard-wrapper">
    <!-- Toggle Navigation - Compact Design -->
    <div class="toggle-header" :class="{ collapsed: toggleCollapsed }">
      <div v-if="!toggleCollapsed" class="toggle-container">
        <div class="toggle-background" :class="{ 'active-dashboard': activeTab === 'dashboard' }"></div>
        <button
          @click="activeTab = 'chat'"
          :class="['toggle-option', { active: activeTab === 'chat' }]"
        >
          <MessageSquareIcon class="w-3.5 h-3.5" />
          <span>Chatbot AI</span>
        </button>
        <button
          @click="activeTab = 'dashboard'"
          :class="['toggle-option', { active: activeTab === 'dashboard' }]"
        >
          <BarChartIcon class="w-3.5 h-3.5" />
          <span>Dashboard</span>
        </button>
      </div>
      
      <!-- Mini Toggle when collapsed -->
      <div v-else class="mini-toggle">
        <button
          @click="activeTab = 'chat'"
          :class="['mini-option', { active: activeTab === 'chat' }]"
          title="Chatbot AI"
        >
          <MessageSquareIcon class="w-3.5 h-3.5" />
        </button>
        <button
          @click="activeTab = 'dashboard'"
          :class="['mini-option', { active: activeTab === 'dashboard' }]"
          title="Dashboard"
        >
          <BarChartIcon class="w-3.5 h-3.5" />
        </button>
      </div>

      <!-- Collapse/Expand Button -->
      <button 
        @click="toggleCollapsed = !toggleCollapsed" 
        class="collapse-btn"
        :title="toggleCollapsed ? 'Mở rộng' : 'Thu gọn'"
      >
        <ChevronUpIcon v-if="!toggleCollapsed" class="w-3.5 h-3.5" />
        <ChevronDownIcon v-else class="w-3.5 h-3.5" />
      </button>
    </div>

    <!-- Tab Content -->
    <div class="content-wrapper">
      <!-- Chat Tab -->
      <div v-show="activeTab === 'chat'" class="content-view chat-view">
        <ChatPage />
      </div>

      <!-- Dashboard Tab -->
      <div v-show="activeTab === 'dashboard'" class="content-view dashboard-view">
        <DashboardAnalytics />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { MessageSquare as MessageSquareIcon, BarChart as BarChartIcon, ChevronUp as ChevronUpIcon, ChevronDown as ChevronDownIcon } from 'lucide-vue-next'
import ChatPage from '@/components/dashboard/ChatWrapper.vue'
import DashboardAnalytics from '@/components/dashboard/DashboardAnalytics.vue'

const activeTab = ref('chat') // Default is Chat
const toggleCollapsed = ref(false) // Toggle collapse state
</script>

<style scoped>
.dashboard-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  overflow: hidden;
}

/* Toggle Header */
.toggle-header {
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  padding: 0.5rem 1rem;
  box-shadow: 0 1px 4px rgba(14, 165, 233, 0.15);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  position: relative;
  transition: all 0.3s ease;
  flex-shrink: 0;
  z-index: 10;
}

/* Mobile responsive for toggle header */
@media (max-width: 640px) {
  .toggle-header {
    padding: 0.5rem 0.75rem;
    gap: 0.5rem;
  }
  
  .toggle-option span {
    font-size: 0.75rem;
  }
  
  .collapse-btn {
    padding: 3px;
  }
}

.toggle-header.collapsed {
  padding: 0.35rem 0.75rem;
}

.toggle-container {
  position: relative;
  display: inline-flex;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 7px;
  padding: 3px;
  gap: 3px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.toggle-background {
  position: absolute;
  top: 3px;
  left: 3px;
  width: calc(50% - 4.5px);
  height: calc(100% - 6px);
  background: white;
  border-radius: 5px;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  z-index: 1;
}

.toggle-background.active-dashboard {
  transform: translateX(calc(100% + 6px));
}

.toggle-option {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 14px;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  color: rgba(255, 255, 255, 0.8);
  border-radius: 5px;
  white-space: nowrap;
  font-size: 0.8125rem;
  font-weight: 500;
}

.toggle-option.active {
  color: #0284c7;
}

.toggle-option:not(.active):hover {
  color: white;
}

/* Mini Toggle */
.mini-toggle {
  display: flex;
  gap: 5px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 5px;
  padding: 3px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.mini-option {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  color: rgba(255, 255, 255, 0.8);
  border-radius: 4px;
}

.mini-option.active {
  background: white;
  color: #0284c7;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.mini-option:not(.active):hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}

/* Collapse Button */
.collapse-btn {
  margin-left: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: white;
}

.collapse-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Content Wrapper */
.content-wrapper {
  flex: 1;
  min-height: 0;
  position: relative;
  overflow: hidden;
  width: 100%;
  height: 100%;
}

/* Mobile responsive for content */
@media (max-width: 1023px) {
  .content-wrapper {
    height: calc(100% - var(--toggle-header-height, 60px));
  }
  
  .content-view {
    width: 100%;
    height: 100%;
  }
}

.content-view {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100%;
  height: 100%;
}

.chat-view {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.dashboard-view {
  overflow-y: auto;
  overflow-x: hidden;
}

/* Custom Scrollbar for Dashboard */
.dashboard-view::-webkit-scrollbar {
  width: 6px;
}

.dashboard-view::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.dashboard-view::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.dashboard-view::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Mobile responsive fixes */
@media (max-width: 1023px) {
  .dashboard-wrapper {
    height: 100vh;
    height: 100dvh; /* Dynamic viewport height for mobile */
    overflow: hidden;
  }
  
  .chat-view {
    width: 100%;
    height: 100%;
    overflow: hidden;
  }
  
  .toggle-option {
    font-size: 0.75rem;
    padding: 4px 10px;
  }
  
  .toggle-option span {
    display: inline;
  }
}
</style>
