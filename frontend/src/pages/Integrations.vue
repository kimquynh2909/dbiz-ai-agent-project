<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b">
      <div class="px-6 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <div
              class="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center"
            >
              <LinkIcon class="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 class="text-2xl font-bold text-gray-900">{{ $t('integrations.pageTitle') }}</h1>
              <p class="text-sm text-gray-500">{{ $t('integrations.pageSubtitle') }}</p>
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <div class="text-right">
              <div class="text-sm text-gray-500">{{ $t('integrations.webhooksActive') }}</div>
              <div class="text-xl font-bold text-gray-900">{{ webhookStats.active }}/{{ webhookStats.total }}</div>
            </div>
            <button
              @click="showWebhookModal = true"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
            >
              <PlusIcon class="w-4 h-4" />
              <span>{{ $t('integrations.createWebhook') }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="bg-white border-b">
      <div class="px-6">
        <nav class="flex space-x-8">
          <button
            v-for="tab in tabsWithBadges"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            ]"
          >
            <div class="flex items-center space-x-2">
              <component :is="tab.icon" class="w-4 h-4" />
              <span>{{ tab.name }}</span>
              <span v-if="tab.badge" class="bg-red-100 text-red-600 text-xs px-2 py-1 rounded-full">
                {{ tab.badge }}
              </span>
            </div>
          </button>
        </nav>
      </div>
    </div>

    <!-- Content Area -->
    <div class="p-6">
      <!-- Overview Tab -->
      <div v-if="activeTab === 'overview'" class="space-y-6">
        <!-- Stats Grid -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div class="bg-white rounded-lg shadow-sm p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600">Active Webhooks</p>
                <p class="text-2xl font-bold text-gray-900">{{ webhookStats.active }}</p>
                <p class="text-xs text-gray-500 mt-1">{{ webhookStats.today }} triggered today</p>
              </div>
              <div class="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                <LinkIcon class="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow-sm p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600">API Endpoints</p>
                <p class="text-2xl font-bold text-gray-900">{{ apiStats.endpoints }}</p>
                <p class="text-xs text-gray-500 mt-1">{{ apiStats.active }} active</p>
              </div>
              <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                <ServerIcon class="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow-sm p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600">Transactions</p>
                <p class="text-2xl font-bold text-gray-900">{{ transactionStats.today }}</p>
                <p class="text-xs text-gray-500 mt-1">{{ transactionStats.success }} successful</p>
              </div>
              <div class="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
                <DatabaseIcon class="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow-sm p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600">Security Alerts</p>
                <p class="text-2xl font-bold text-red-600">{{ securityStats.alerts }}</p>
                <p class="text-xs text-gray-500 mt-1">{{ securityStats.failedAttempts }} failed attempts</p>
              </div>
              <div class="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center">
                <UsersIcon class="w-6 h-6 text-red-600" />
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Recent Webhooks -->
          <div class="bg-white rounded-lg shadow-sm p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">Recent Webhooks</h3>
              <button @click="activeTab = 'webhooks'" class="text-blue-600 hover:text-blue-700 text-sm">
                View all
              </button>
            </div>
            <div class="space-y-3">
              <div
                v-for="webhook in webhooks.slice(0, 3)"
                :key="webhook.id"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div class="flex items-center space-x-3">
                  <div
                    :class="['w-3 h-3 rounded-full', webhook.status === 'active' ? 'bg-green-500' : 'bg-gray-300']"
                  ></div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ webhook.name }}</p>
                    <p class="text-xs text-gray-500">{{ webhook.lastTriggered || 'Chưa có' }}</p>
                  </div>
                </div>
                <span class="text-xs text-gray-500">{{ webhook.method }}</span>
              </div>
            </div>
          </div>

          <!-- Recent Transactions -->
          <div class="bg-white rounded-lg shadow-sm p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">Recent Transactions</h3>
              <button @click="activeTab = 'transactions'" class="text-blue-600 hover:text-blue-700 text-sm">
                View all
              </button>
            </div>
            <div class="space-y-3">
              <div
                v-for="transaction in recentTransactions.slice(0, 3)"
                :key="transaction.id"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div class="flex items-center space-x-3">
                  <div
                    :class="[
                      'w-3 h-3 rounded-full',
                      transaction.status === 'success'
                        ? 'bg-green-500'
                        : transaction.status === 'pending'
                        ? 'bg-yellow-500'
                        : 'bg-red-500',
                    ]"
                  ></div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ transaction.description }}</p>
                    <p class="text-xs text-gray-500">{{ transaction.timestamp }}</p>
                  </div>
                </div>
                <div class="text-right">
                  <div
                    :class="[
                      'text-xs font-medium',
                      transaction.status === 'success'
                        ? 'text-green-600'
                        : transaction.status === 'pending'
                        ? 'text-yellow-600'
                        : 'text-red-600',
                    ]"
                  >
                    {{ transaction.status.toUpperCase() }}
                  </div>
                  <div class="text-xs text-gray-500">{{ transaction.duration }}ms</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Webhooks Tab -->
      <div v-if="activeTab === 'webhooks'" class="space-y-6">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-bold text-gray-900">{{ $t('integrations.webhookManagement') }}</h2>
          <button
            @click="showWebhookModal = true"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
          >
            <PlusIcon class="w-4 h-4" />
            <span>Tạo Webhook</span>
          </button>
        </div>

        <div class="bg-white rounded-lg shadow-sm">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Webhook
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Events</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Triggered
                  </th>
                  <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="webhook in webhooks" :key="webhook.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div class="text-sm font-medium text-gray-900">{{ webhook.name }}</div>
                      <div class="text-sm text-gray-500">{{ webhook.url }}</div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div
                      :class="[
                        'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                        webhook.status === 'active'
                          ? 'bg-green-100 text-green-800'
                          : webhook.status === 'inactive'
                          ? 'bg-gray-100 text-gray-800'
                          : 'bg-red-100 text-red-800',
                      ]"
                    >
                      {{
                        webhook.status === 'active' ? 'Active' : webhook.status === 'inactive' ? 'Inactive' : 'Error'
                      }}
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900">{{ webhook.events.slice(0, 2).join(', ') }}</div>
                    <div v-if="webhook.events.length > 2" class="text-xs text-gray-500">
                      +{{ webhook.events.length - 2 }} more
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ webhook.lastTriggered || 'Never' }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div class="flex items-center justify-end space-x-2">
                      <button @click="testWebhook(webhook)" class="text-blue-600 hover:text-blue-900">Test</button>
                      <button @click="editWebhook(webhook)" class="text-gray-600 hover:text-gray-900">Edit</button>
                      <button
                        @click="toggleWebhookStatus(webhook)"
                        :class="[
                          webhook.status === 'active'
                            ? 'text-red-600 hover:text-red-900'
                            : 'text-green-600 hover:text-green-900',
                        ]"
                      >
                        {{ webhook.status === 'active' ? 'Disable' : 'Enable' }}
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- API Endpoints Tab -->
      <div v-if="activeTab === 'endpoints'" class="space-y-6">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-bold text-gray-900">API Endpoints</h2>
          <button
            @click="showApiModal = true"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
          >
            <PlusIcon class="w-4 h-4" />
            <span>Tạo Endpoint</span>
          </button>
        </div>

        <div class="bg-white rounded-lg shadow-sm">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Endpoint
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Method</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rate Limit
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Used
                  </th>
                  <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="endpoint in apiEndpoints" :key="endpoint.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div class="text-sm font-medium text-gray-900">{{ endpoint.name }}</div>
                      <div class="text-sm text-gray-500">{{ endpoint.url }}</div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span class="inline-flex px-2 py-1 text-xs font-semibold bg-blue-100 text-blue-800 rounded-full">
                      {{ endpoint.method }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div
                      :class="[
                        'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                        endpoint.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800',
                      ]"
                    >
                      {{ endpoint.status === 'active' ? 'Active' : 'Inactive' }}
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ endpoint.rateLimit }}/min</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ endpoint.lastUsed || 'Never' }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div class="flex items-center justify-end space-x-2">
                      <button @click="testEndpoint(endpoint)" class="text-blue-600 hover:text-blue-900">Test</button>
                      <button @click="editEndpoint(endpoint)" class="text-gray-600 hover:text-gray-900">Edit</button>
                      <button
                        @click="toggleEndpointStatus(endpoint)"
                        :class="[
                          endpoint.status === 'active'
                            ? 'text-red-600 hover:text-red-900'
                            : 'text-green-600 hover:text-green-900',
                        ]"
                      >
                        {{ endpoint.status === 'active' ? 'Disable' : 'Enable' }}
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Transactions Tab -->
      <div v-if="activeTab === 'transactions'" class="space-y-6">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-bold text-gray-900">Transactions</h2>
          <button
            @click="refreshTransactions"
            class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Refresh
          </button>
        </div>

        <div class="bg-white rounded-lg shadow-sm">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Description
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Duration
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Timestamp
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="transaction in recentTransactions" :key="transaction.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">{{ transaction.description }}</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div
                      :class="[
                        'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                        transaction.status === 'success'
                          ? 'bg-green-100 text-green-800'
                          : transaction.status === 'pending'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800',
                      ]"
                    >
                      {{ transaction.status.toUpperCase() }}
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ transaction.duration }}ms</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ transaction.timestamp }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Audit Logs Tab -->
      <div v-if="activeTab === 'logs'" class="space-y-6">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-bold text-gray-900">Audit Logs</h2>
          <button
            @click="refreshAuditLogs"
            class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Refresh
          </button>
        </div>

        <div class="bg-white rounded-lg shadow-sm">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Level</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">IP</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Timestamp
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="log in auditLogs" :key="log.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div class="text-sm font-medium text-gray-900">{{ log.action }}</div>
                      <div class="text-sm text-gray-500">{{ log.message }}</div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span
                      :class="[
                        'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                        log.level === 'info'
                          ? 'bg-blue-100 text-blue-800'
                          : log.level === 'warning'
                          ? 'bg-yellow-100 text-yellow-800'
                          : log.level === 'error'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-green-100 text-green-800',
                      ]"
                    >
                      {{ log.level.toUpperCase() }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ log.user }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ log.ip }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ log.timestamp }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Security Tab -->
      <div v-if="activeTab === 'security'" class="space-y-6">
        <h2 class="text-xl font-bold text-gray-900">Security Monitoring</h2>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="bg-white rounded-lg shadow-sm p-6">
            <h3 class="font-medium text-gray-900 mb-4">Authentication Status</h3>
            <div class="space-y-3">
              <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p class="font-medium text-gray-900">JWT Tokens</p>
                  <p class="text-sm text-gray-500">Active sessions</p>
                </div>
                <div class="flex items-center space-x-2">
                  <div class="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span class="text-sm text-green-600">{{ securityStats.jwtTokens }}</span>
                </div>
              </div>
              <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p class="font-medium text-gray-900">API Keys</p>
                  <p class="text-sm text-gray-500">Active keys</p>
                </div>
                <div class="flex items-center space-x-2">
                  <div class="w-3 h-3 bg-blue-500 rounded-full"></div>
                  <span class="text-sm text-blue-600">{{ securityStats.apiKeys }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow-sm p-6">
            <h3 class="font-medium text-gray-900 mb-4">Rate Limiting</h3>
            <div class="space-y-3">
              <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span class="text-sm text-gray-700">Requests/minute</span>
                <span class="font-medium text-gray-900">{{ securityStats.rateLimit }}</span>
              </div>
              <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span class="text-sm text-gray-700">Blocked requests</span>
                <span class="font-medium text-red-600">{{ securityStats.blockedRequests }}</span>
              </div>
              <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span class="text-sm text-gray-700">IP restrictions</span>
                <span class="font-medium text-gray-900">{{ securityStats.ipRestrictions }}</span>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow-sm p-6">
            <h3 class="font-medium text-gray-900 mb-4">Threat Detection</h3>
            <div class="space-y-3">
              <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span class="text-sm text-gray-700">Suspicious activities</span>
                <span class="font-medium text-yellow-600">{{ securityStats.suspiciousActivities }}</span>
              </div>
              <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span class="text-sm text-gray-700">Failed attempts</span>
                <span class="font-medium text-red-600">{{ securityStats.failedAttempts }}</span>
              </div>
              <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span class="text-sm text-gray-700">Last security scan</span>
                <span class="font-medium text-gray-900">{{ securityStats.lastScan }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Webhook Modal -->
    <div v-if="showWebhookModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between p-6 border-b">
          <h3 class="text-lg font-bold text-gray-900">Tạo Webhook mới</h3>
          <button @click="closeWebhookModal" class="text-gray-400 hover:text-gray-600">
            <XIcon class="w-6 h-6" />
          </button>
        </div>
        <div class="p-6">
          <form @submit.prevent="saveWebhook" class="space-y-6">
            <!-- Basic Information -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Tên Webhook *</label>
                <input
                  type="text"
                  v-model="webhookForm.name"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="VD: ERP Data Sync"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">HTTP Method *</label>
                <select
                  v-model="webhookForm.method"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="POST">POST</option>
                  <option value="PUT">PUT</option>
                  <option value="PATCH">PATCH</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Mô tả</label>
              <textarea
                v-model="webhookForm.description"
                rows="2"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Mô tả chức năng của webhook này..."
              ></textarea>
            </div>

            <!-- URL Configuration -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Webhook URL *</label>
              <input
                type="url"
                v-model="webhookForm.url"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="https://your-system.com/api/webhook"
              />
            </div>

            <!-- Events Configuration -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-3">Sự kiện kích hoạt *</label>
              <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                <label v-for="event in availableEvents" :key="event.value" class="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    :value="event.value"
                    v-model="webhookForm.events"
                    class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span class="text-sm text-gray-700">{{ event.label }}</span>
                </label>
              </div>
            </div>

            <!-- Security Settings -->
            <div class="border-t pt-6">
              <h4 class="text-md font-semibold text-gray-900 mb-4">{{ $t('integrations.securitySettings') }}</h4>
              <div class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Authentication Type</label>
                    <select
                      v-model="webhookForm.authType"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="none">Không xác thực</option>
                      <option value="bearer">Bearer Token</option>
                      <option value="basic">Basic Auth</option>
                      <option value="hmac">HMAC Signature</option>
                    </select>
                  </div>
                  <div v-if="webhookForm.authType === 'bearer'">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Bearer Token</label>
                    <input
                      type="password"
                      v-model="webhookForm.authToken"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="your-bearer-token"
                    />
                  </div>
                </div>

                <div v-if="webhookForm.authType === 'basic'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Username</label>
                    <input
                      type="text"
                      v-model="webhookForm.authUsername"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="username"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Password</label>
                    <input
                      type="password"
                      v-model="webhookForm.authPassword"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="password"
                    />
                  </div>
                </div>

                <div v-if="webhookForm.authType === 'hmac'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Secret Key</label>
                    <input
                      type="password"
                      v-model="webhookForm.hmacSecret"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="your-secret-key"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Algorithm</label>
                    <select
                      v-model="webhookForm.hmacAlgorithm"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="sha256">SHA-256</option>
                      <option value="sha512">SHA-512</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <!-- Advanced Settings -->
            <div class="border-t pt-6">
              <h4 class="text-md font-semibold text-gray-900 mb-4">{{ $t('integrations.advancedSettings') }}</h4>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Timeout (seconds)</label>
                  <input
                    type="number"
                    v-model.number="webhookForm.timeout"
                    min="1"
                    max="300"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Retry Attempts</label>
                  <input
                    type="number"
                    v-model.number="webhookForm.retries"
                    min="0"
                    max="10"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Rate Limit (req/min)</label>
                  <input
                    type="number"
                    v-model.number="webhookForm.rateLimit"
                    min="1"
                    max="1000"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>

            <!-- JSON Schema Validation -->
            <div class="border-t pt-6">
              <h4 class="text-md font-semibold text-gray-900 mb-4">JSON Schema Validation</h4>
              <div class="space-y-4">
                <div class="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    v-model="webhookForm.enableValidation"
                    id="enableValidation"
                    class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label for="enableValidation" class="text-sm text-gray-700">Bật validation JSON schema</label>
                </div>
                <div v-if="webhookForm.enableValidation">
                  <label class="block text-sm font-medium text-gray-700 mb-2">JSON Schema</label>
                  <textarea
                    v-model="webhookForm.jsonSchema"
                    rows="8"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                    placeholder='{
  "type": "object",
  "properties": {
    "event": {"type": "string"},
    "data": {"type": "object"}
  },
  "required": ["event", "data"]
}'
                  ></textarea>
                  <p class="text-xs text-gray-500 mt-1">Định nghĩa cấu trúc JSON mà webhook sẽ nhận</p>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex space-x-3 pt-6 border-t">
              <button
                type="button"
                @click="testWebhookForm"
                class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Test Webhook
              </button>
              <button
                type="submit"
                class="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                Tạo Webhook
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
import {
  Link as LinkIcon,
  Database as DatabaseIcon,
  Users as UsersIcon,
  Server as ServerIcon,
  X as XIcon,
  Plus as PlusIcon,
} from 'lucide-vue-next'
import { useNotificationStore } from '@/stores/notifications'

const notificationStore = useNotificationStore()

const showWebhookModal = ref(false)
const showApiModal = ref(false)
const showTransactionsModal = ref(false)
const editingWebhook = ref(null)
const editingEndpoint = ref(null)
const activeTab = ref('overview')

// Navigation tabs
const tabs = ref([
  { id: 'overview', name: 'Overview', icon: 'DatabaseIcon', badge: null },
  { id: 'webhooks', name: 'Webhooks', icon: 'LinkIcon', badge: null },
  { id: 'endpoints', name: 'API Endpoints', icon: 'ServerIcon', badge: null },
  { id: 'transactions', name: 'Transactions', icon: 'DatabaseIcon', badge: null },
  { id: 'logs', name: 'Audit Logs', icon: 'UsersIcon', badge: null },
  { id: 'security', name: 'Security', icon: 'UsersIcon', badge: null },
])

// Statistics
const webhookStats = ref({
  active: 3,
  total: 5,
  today: 47,
})

const apiStats = ref({
  endpoints: 12,
  active: 10,
  rateLimited: 2,
})

const transactionStats = ref({
  today: 1247,
  success: 1180,
  failed: 67,
  pending: 12,
})

const securityStats = ref({
  alerts: 3,
  jwtTokens: 45,
  apiKeys: 8,
  rateLimit: 100,
  blockedRequests: 23,
  ipRestrictions: 5,
  suspiciousActivities: 7,
  failedAttempts: 12,
  lastScan: '2 giờ trước',
})

// Computed property to update tabs with dynamic badges
const tabsWithBadges = computed(() => {
  return tabs.value.map((tab) => {
    if (tab.id === 'security') {
      return {
        ...tab,
        badge: securityStats.value.alerts > 0 ? securityStats.value.alerts : null,
      }
    }
    return tab
  })
})

// Webhook Management
const webhooks = ref([
  {
    id: 1,
    name: 'ERP Data Sync',
    description: 'Đồng bộ dữ liệu từ ERP system',
    url: 'https://erp.company.com/api/webhook/sync',
    method: 'POST',
    status: 'active',
    events: ['data.created', 'data.updated'],
    lastTriggered: '2 phút trước',
    authType: 'bearer',
    timeout: 30,
    retries: 3,
    rateLimit: 100,
  },
  {
    id: 2,
    name: 'CRM Lead Notification',
    description: 'Thông báo khi có lead mới từ CRM',
    url: 'https://crm.company.com/api/webhook/leads',
    method: 'POST',
    status: 'active',
    events: ['lead.created', 'lead.updated'],
    lastTriggered: '5 phút trước',
    authType: 'hmac',
    timeout: 15,
    retries: 2,
    rateLimit: 50,
  },
  {
    id: 3,
    name: 'Error Monitoring',
    description: 'Gửi thông báo lỗi hệ thống',
    url: 'https://monitoring.company.com/api/alerts',
    method: 'POST',
    status: 'inactive',
    events: ['error.critical', 'error.warning'],
    lastTriggered: '1 giờ trước',
    authType: 'basic',
    timeout: 10,
    retries: 5,
    rateLimit: 200,
  },
])

const availableEvents = ref([
  { value: 'data.created', label: 'Data Created' },
  { value: 'data.updated', label: 'Data Updated' },
  { value: 'data.deleted', label: 'Data Deleted' },
  { value: 'user.created', label: 'User Created' },
  { value: 'user.updated', label: 'User Updated' },
  { value: 'lead.created', label: 'Lead Created' },
  { value: 'lead.updated', label: 'Lead Updated' },
  { value: 'order.created', label: 'Order Created' },
  { value: 'order.updated', label: 'Order Updated' },
  { value: 'error.critical', label: 'Critical Error' },
  { value: 'error.warning', label: 'Warning' },
  { value: 'system.maintenance', label: 'System Maintenance' },
])

const webhookForm = ref({
  name: '',
  description: '',
  url: '',
  method: 'POST',
  events: [],
  authType: 'none',
  authToken: '',
  authUsername: '',
  authPassword: '',
  hmacSecret: '',
  hmacAlgorithm: 'sha256',
  timeout: 30,
  retries: 3,
  rateLimit: 100,
  enableValidation: false,
  jsonSchema: '',
})

// API Endpoints
const apiEndpoints = ref([
  {
    id: 1,
    name: 'User Management API',
    description: 'API để quản lý người dùng và phân quyền',
    url: '/api/v1/users',
    method: 'GET',
    status: 'active',
    rateLimit: 100,
    lastUsed: '2 phút trước',
  },
  {
    id: 2,
    name: 'Data Sync Endpoint',
    description: 'Endpoint để đồng bộ dữ liệu từ external systems',
    url: '/api/v1/sync',
    method: 'POST',
    status: 'active',
    rateLimit: 50,
    lastUsed: '5 phút trước',
  },
  {
    id: 3,
    name: 'Webhook Receiver',
    description: 'Nhận webhook từ các hệ thống bên ngoài',
    url: '/api/v1/webhook',
    method: 'POST',
    status: 'inactive',
    rateLimit: 200,
    lastUsed: '1 giờ trước',
  },
])

// Audit Logs
const auditLogs = ref([
  {
    id: 1,
    level: 'info',
    action: 'Webhook Created',
    message: 'New webhook "ERP Data Sync" created successfully',
    user: 'admin@system.com',
    timestamp: '2 phút trước',
    ip: '192.168.1.100',
  },
  {
    id: 2,
    level: 'success',
    action: 'API Endpoint Tested',
    message: 'API endpoint test completed successfully',
    user: 'admin@system.com',
    timestamp: '5 phút trước',
    ip: '192.168.1.100',
  },
  {
    id: 3,
    level: 'warning',
    action: 'Rate Limit Exceeded',
    message: 'Rate limit exceeded for IP 203.0.113.1',
    user: 'system',
    timestamp: '8 phút trước',
    ip: '203.0.113.1',
  },
  {
    id: 4,
    level: 'error',
    action: 'Authentication Failed',
    message: 'Invalid API key provided for webhook endpoint',
    user: 'system',
    timestamp: '12 phút trước',
    ip: '198.51.100.42',
  },
])

// Recent Transactions
const recentTransactions = ref([
  {
    id: 1,
    description: 'Webhook delivery to ERP system',
    status: 'success',
    timestamp: '2 phút trước',
    duration: 145,
  },
  {
    id: 2,
    description: 'Data sync with CRM system',
    status: 'success',
    timestamp: '5 phút trước',
    duration: 234,
  },
  {
    id: 3,
    description: 'API authentication request',
    status: 'pending',
    timestamp: '8 phút trước',
    duration: 89,
  },
  {
    id: 4,
    description: 'Webhook validation check',
    status: 'failed',
    timestamp: '12 phút trước',
    duration: 0,
  },
])

// API Endpoint Functions
const testEndpoint = async (endpoint) => {
  try {
    notificationStore.notify(`Endpoint test thành công!\nURL: ${endpoint.url}\nMethod: ${endpoint.method}`, 'success')

    endpoint.lastUsed = 'Vừa test'

    // Add to audit logs
    auditLogs.value.unshift({
      id: Date.now(),
      level: 'info',
      action: 'API Endpoint Tested',
      message: `Endpoint "${endpoint.name}" tested successfully`,
      user: 'admin@system.com',
      timestamp: 'Vừa xong',
      ip: '192.168.1.100',
    })
  } catch (error) {
    notificationStore.notify('Endpoint test thất bại: ' + error.message, 'error')
  }
}

const editEndpoint = (endpoint) => {
  editingEndpoint.value = endpoint
  showApiModal.value = true
}

const toggleEndpointStatus = (endpoint) => {
  endpoint.status = endpoint.status === 'active' ? 'inactive' : 'active'

  // Add to audit logs
  auditLogs.value.unshift({
    id: Date.now(),
    level: 'info',
    action: 'Endpoint Status Changed',
    message: `Endpoint "${endpoint.name}" ${endpoint.status === 'active' ? 'activated' : 'deactivated'}`,
    user: 'admin@system.com',
    timestamp: 'Vừa xong',
    ip: '192.168.1.100',
  })
}

const refreshAuditLogs = () => {
  // Simulate refresh

  // Add refresh log
  auditLogs.value.unshift({
    id: Date.now(),
    level: 'info',
    action: 'Audit Logs Refreshed',
    message: 'Audit logs refreshed by user',
    user: 'admin@system.com',
    timestamp: 'Vừa xong',
    ip: '192.168.1.100',
  })
}

const refreshTransactions = () => {
  // Simulate refresh

  // Add new transaction for demo
  recentTransactions.value.unshift({
    id: Date.now(),
    description: 'System refresh triggered',
    status: 'success',
    timestamp: 'Vừa xong',
    duration: 50,
  })
}

// Webhook Management Functions
const closeWebhookModal = () => {
  showWebhookModal.value = false
  editingWebhook.value = null
  resetWebhookForm()
}

const resetWebhookForm = () => {
  webhookForm.value = {
    name: '',
    description: '',
    url: '',
    method: 'POST',
    events: [],
    authType: 'none',
    authToken: '',
    authUsername: '',
    authPassword: '',
    hmacSecret: '',
    hmacAlgorithm: 'sha256',
    timeout: 30,
    retries: 3,
    rateLimit: 100,
    enableValidation: false,
    jsonSchema: '',
  }
}

const saveWebhook = () => {
  // Validate JSON Schema if enabled
  if (webhookForm.value.enableValidation && webhookForm.value.jsonSchema) {
    try {
      JSON.parse(webhookForm.value.jsonSchema)
    } catch (error) {
      notificationStore.notify('JSON Schema không hợp lệ: ' + error.message, 'error')
      return
    }
  }

  // Validate required fields
  if (!webhookForm.value.name || !webhookForm.value.url || webhookForm.value.events.length === 0) {
    notificationStore.notify('Vui lòng điền đầy đủ thông tin bắt buộc', 'warning')
    return
  }

  const webhookData = {
    ...webhookForm.value,
    id: editingWebhook.value?.id || Date.now(),
    status: 'active',
    lastTriggered: null,
  }

  if (editingWebhook.value) {
    // Update existing webhook
    const index = webhooks.value.findIndex((w) => w.id === editingWebhook.value.id)
    if (index > -1) {
      webhooks.value[index] = webhookData
    }
  } else {
    // Create new webhook
    webhooks.value.unshift(webhookData)
  }

  // Add to audit logs
  auditLogs.value.unshift({
    id: Date.now(),
    level: 'success',
    action: editingWebhook.value ? 'Webhook Updated' : 'Webhook Created',
    message: `Webhook "${webhookData.name}" ${editingWebhook.value ? 'updated' : 'created'} successfully`,
    user: 'admin@system.com',
    timestamp: 'Vừa xong',
    ip: '192.168.1.100',
  })

  closeWebhookModal()
}

const editWebhook = (webhook) => {
  editingWebhook.value = webhook
  webhookForm.value = {
    name: webhook.name,
    description: webhook.description,
    url: webhook.url,
    method: webhook.method,
    events: [...webhook.events],
    authType: webhook.authType || 'none',
    authToken: '',
    authUsername: '',
    authPassword: '',
    hmacSecret: '',
    hmacAlgorithm: 'sha256',
    timeout: webhook.timeout || 30,
    retries: webhook.retries || 3,
    rateLimit: webhook.rateLimit || 100,
    enableValidation: false,
    jsonSchema: '',
  }
  showWebhookModal.value = true
}

const testWebhook = async (webhook) => {
  try {
    // Simulate webhook test
    const testPayload = {
      event: 'test',
      data: {
        message: 'Test webhook from integration system',
        timestamp: new Date().toISOString(),
      },
    }

    // Here you would make actual HTTP request to test the webhook

    // Simulate success response
    notificationStore.notify(`Webhook test thành công!\nURL: ${webhook.url}\nMethod: ${webhook.method}`, 'success')

    // Update last triggered time
    webhook.lastTriggered = 'Vừa test'

    // Add to audit logs
    auditLogs.value.unshift({
      id: Date.now(),
      level: 'info',
      action: 'Webhook Tested',
      message: `Webhook "${webhook.name}" tested successfully`,
      user: 'admin@system.com',
      timestamp: 'Vừa xong',
      ip: '192.168.1.100',
    })
  } catch (error) {
    notificationStore.notify('Webhook test thất bại: ' + error.message, 'error')

    // Add error to audit logs
    auditLogs.value.unshift({
      id: Date.now(),
      level: 'error',
      action: 'Webhook Test Failed',
      message: `Webhook "${webhook.name}" test failed: ${error.message}`,
      user: 'admin@system.com',
      timestamp: 'Vừa xong',
      ip: '192.168.1.100',
    })
  }
}

const testWebhookForm = () => {
  if (!webhookForm.value.url) {
    notificationStore.notify('Vui lòng nhập Webhook URL', 'warning')
    return
  }

  // Simulate form validation test
  const testData = {
    url: webhookForm.value.url,
    method: webhookForm.value.method,
    events: webhookForm.value.events,
    authType: webhookForm.value.authType,
  }

  notificationStore.notify('Webhook configuration hợp lệ!\nSẵn sàng để tạo webhook.', 'success')
}

const toggleWebhookStatus = (webhook) => {
  webhook.status = webhook.status === 'active' ? 'inactive' : 'active'

  // Add to audit logs
  auditLogs.value.unshift({
    id: Date.now(),
    level: webhook.status === 'active' ? 'success' : 'warning',
    action: 'Webhook Status Changed',
    message: `Webhook "${webhook.name}" ${webhook.status === 'active' ? 'activated' : 'deactivated'}`,
    user: 'admin@system.com',
    timestamp: 'Vừa xong',
    ip: '192.168.1.100',
  })
}

onMounted(() => {})
</script>
