<template>
  <div class="cron-selector">
    <div class="cron-preview">
      <h4>当前表达式: {{ cronExpression }}</h4>
      <p class="preview-text">预览: {{ cronPreview }}</p>
    </div>

    <el-tabs v-model="activeTab" class="cron-tabs">
      <!-- 常用配置 -->
      <el-tab-pane label="常用配置" name="presets">
        <div class="preset-list">
          <div class="preset-group">
            <h5>按小时执行</h5>
            <div class="preset-buttons">
              <el-button
                v-for="preset in hourPresets"
                :key="preset.value"
                size="small"
                :type="cronExpression === preset.value ? 'primary' : 'default'"
                @click="selectPreset(preset.value)"
              >
                {{ preset.label }}
              </el-button>
            </div>
          </div>

          <div class="preset-group">
            <h5>按日执行</h5>
            <div class="preset-buttons">
              <el-button
                v-for="preset in dayPresets"
                :key="preset.value"
                size="small"
                :type="cronExpression === preset.value ? 'primary' : 'default'"
                @click="selectPreset(preset.value)"
              >
                {{ preset.label }}
              </el-button>
            </div>
          </div>

          <div class="preset-group">
            <h5>按周执行</h5>
            <div class="preset-buttons">
              <el-button
                v-for="preset in weekPresets"
                :key="preset.value"
                size="small"
                :type="cronExpression === preset.value ? 'primary' : 'default'"
                @click="selectPreset(preset.value)"
              >
                {{ preset.label }}
              </el-button>
            </div>
          </div>

          <div class="preset-group">
            <h5>按月执行</h5>
            <div class="preset-buttons">
              <el-button
                v-for="preset in monthPresets"
                :key="preset.value"
                size="small"
                :type="cronExpression === preset.value ? 'primary' : 'default'"
                @click="selectPreset(preset.value)"
              >
                {{ preset.label }}
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 自定义配置 -->
      <el-tab-pane label="自定义配置" name="custom">
        <div class="custom-config">
          <el-row :gutter="20">
            <!-- 分钟 -->
            <el-col :span="4">
              <div class="field-group">
                <label>分钟</label>
                <el-select
                  v-model="fields.minute"
                  placeholder="分钟"
                  size="small"
                  @change="updateExpression"
                >
                  <el-option label="每分钟" value="*" />
                  <el-option label="每5分钟" value="*/5" />
                  <el-option label="每10分钟" value="*/10" />
                  <el-option label="每15分钟" value="*/15" />
                  <el-option label="每30分钟" value="*/30" />
                  <el-option-group label="指定分钟">
                    <el-option
                      v-for="min in minuteOptions"
                      :key="min"
                      :label="min.toString()"
                      :value="min.toString()"
                    />
                  </el-option-group>
                </el-select>
              </div>
            </el-col>

            <!-- 小时 -->
            <el-col :span="4">
              <div class="field-group">
                <label>小时</label>
                <el-select
                  v-model="fields.hour"
                  placeholder="小时"
                  size="small"
                  @change="updateExpression"
                >
                  <el-option label="每小时" value="*" />
                  <el-option label="每2小时" value="*/2" />
                  <el-option label="每6小时" value="*/6" />
                  <el-option label="每12小时" value="*/12" />
                  <el-option-group label="指定小时">
                    <el-option
                      v-for="hour in hourOptions"
                      :key="hour"
                      :label="hour.toString()"
                      :value="hour.toString()"
                    />
                  </el-option-group>
                </el-select>
              </div>
            </el-col>

            <!-- 日 -->
            <el-col :span="4">
              <div class="field-group">
                <label>日</label>
                <el-select
                  v-model="fields.day"
                  placeholder="日"
                  size="small"
                  @change="updateExpression"
                >
                  <el-option label="每天" value="*" />
                  <el-option label="每月1日" value="1" />
                  <el-option label="每月15日" value="15" />
                  <el-option label="每月最后一天" value="L" />
                  <el-option-group label="指定日期">
                    <el-option
                      v-for="day in dayOptions"
                      :key="day"
                      :label="day.toString()"
                      :value="day.toString()"
                    />
                  </el-option-group>
                </el-select>
              </div>
            </el-col>

            <!-- 月 -->
            <el-col :span="4">
              <div class="field-group">
                <label>月</label>
                <el-select
                  v-model="fields.month"
                  placeholder="月"
                  size="small"
                  @change="updateExpression"
                >
                  <el-option label="每月" value="*" />
                  <el-option-group label="指定月份">
                    <el-option
                      v-for="month in monthOptions"
                      :key="month.value"
                      :label="month.label"
                      :value="month.value"
                    />
                  </el-option-group>
                </el-select>
              </div>
            </el-col>

            <!-- 星期 -->
            <el-col :span="4">
              <div class="field-group">
                <label>星期</label>
                <el-select
                  v-model="fields.weekday"
                  placeholder="星期"
                  size="small"
                  @change="updateExpression"
                >
                  <el-option label="每天" value="*" />
                  <el-option-group label="指定星期">
                    <el-option
                      v-for="weekday in weekdayOptions"
                      :key="weekday.value"
                      :label="weekday.label"
                      :value="weekday.value"
                    />
                  </el-option-group>
                </el-select>
              </div>
            </el-col>
          </el-row>

          <div class="custom-help">
            <p><strong>字段说明：</strong></p>
            <ul>
              <li><strong>分钟：</strong>0-59</li>
              <li><strong>小时：</strong>0-23</li>
              <li><strong>日：</strong>1-31（L表示最后一天）</li>
              <li><strong>月：</strong>1-12</li>
              <li><strong>星期：</strong>0-7（0和7都表示周日）</li>
            </ul>
            <p><strong>特殊字符：</strong></p>
            <ul>
              <li><code>*</code> - 匹配任何值</li>
              <li><code>*/n</code> - 每n个单位执行一次</li>
              <li><code>L</code> - 最后一天（仅用于日字段）</li>
            </ul>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <div class="cron-actions">
      <el-button @click="$emit('cancel')">取消</el-button>
      <el-button type="primary" @click="handleConfirm">确定</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'

// Props
interface Props {
  modelValue: string
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: string]
  'confirm': [expression: string]
  'cancel': []
}>()

// 响应式数据
const activeTab = ref('presets')
const fields = reactive({
  minute: '0',
  hour: '2',
  day: '*',
  month: '*',
  weekday: '*'
})

// 计算属性
const cronExpression = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const cronPreview = computed(() => {
  return parseCronExpression(cronExpression.value)
})

// 预设配置
const hourPresets = [
  { label: '每小时', value: '0 * * * *' },
  { label: '每2小时', value: '0 */2 * * *' },
  { label: '每6小时', value: '0 */6 * * *' },
  { label: '每12小时', value: '0 */12 * * *' }
]

const dayPresets = [
  { label: '每天凌晨2点', value: '0 2 * * *' },
  { label: '每天上午9点', value: '0 9 * * *' },
  { label: '每天中午12点', value: '0 12 * * *' },
  { label: '每天晚上6点', value: '0 18 * * *' },
  { label: '每天晚上10点', value: '0 22 * * *' }
]

const weekPresets = [
  { label: '每周一凌晨2点', value: '0 2 * * 1' },
  { label: '每周五下午5点', value: '0 17 * * 5' },
  { label: '工作日每天上午9点', value: '0 9 * * 1-5' },
  { label: '周末每天上午10点', value: '0 10 * * 0,6' }
]

const monthPresets = [
  { label: '每月1日凌晨2点', value: '0 2 1 * *' },
  { label: '每月15日凌晨2点', value: '0 2 15 * *' },
  { label: '每月最后一天凌晨2点', value: '0 2 L * *' }
]

// 选项数据
const minuteOptions = Array.from({ length: 60 }, (_, i) => i)
const hourOptions = Array.from({ length: 24 }, (_, i) => i)
const dayOptions = Array.from({ length: 31 }, (_, i) => i + 1)

const monthOptions = [
  { label: '一月', value: '1' },
  { label: '二月', value: '2' },
  { label: '三月', value: '3' },
  { label: '四月', value: '4' },
  { label: '五月', value: '5' },
  { label: '六月', value: '6' },
  { label: '七月', value: '7' },
  { label: '八月', value: '8' },
  { label: '九月', value: '9' },
  { label: '十月', value: '10' },
  { label: '十一月', value: '11' },
  { label: '十二月', value: '12' }
]

const weekdayOptions = [
  { label: '周日', value: '0' },
  { label: '周一', value: '1' },
  { label: '周二', value: '2' },
  { label: '周三', value: '3' },
  { label: '周四', value: '4' },
  { label: '周五', value: '5' },
  { label: '周六', value: '6' }
]

// 方法
const parseCronExpression = (cron: string) => {
  try {
    const parts = cron.split(' ')
    if (parts.length !== 5) return '格式错误'

    const [minute, hour, day, , weekday] = parts

    if (minute === '0' && hour !== '*') {
      if (day === '*') {
        if (weekday === '*') {
          return `每天${parseInt(hour)}点执行`
        } else {
          const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
          const weekdayNames = weekday.split(',').map(w => weekdays[parseInt(w) % 7]).join('、')
          return `每周${weekdayNames}${parseInt(hour)}点执行`
        }
      } else if (day === 'L') {
        return `每月最后一天${parseInt(hour)}点执行`
      } else if (day !== '*') {
        return `每月${day}日${parseInt(hour)}点执行`
      }
    }

    if (hour === '*/2') {
      return '每2小时执行一次'
    }
    if (hour === '*/6') {
      return '每6小时执行一次'
    }
    if (hour === '*/12') {
      return '每12小时执行一次'
    }

    if (minute === '*/30') {
      return '每30分钟执行一次'
    }
    if (minute === '*/15') {
      return '每15分钟执行一次'
    }
    if (minute === '*/10') {
      return '每10分钟执行一次'
    }
    if (minute === '*/5') {
      return '每5分钟执行一次'
    }

    return '已配置'
  } catch {
    return '解析失败'
  }
}

const selectPreset = (expression: string) => {
  cronExpression.value = expression
  parseExpressionToFields(expression)
}

const parseExpressionToFields = (expression: string) => {
  const parts = expression.split(' ')
  if (parts.length === 5) {
    fields.minute = parts[0]
    fields.hour = parts[1]
    fields.day = parts[2]
    fields.month = parts[3]
    fields.weekday = parts[4]
  }
}

const updateExpression = () => {
  const expression = `${fields.minute} ${fields.hour} ${fields.day} ${fields.month} ${fields.weekday}`
  cronExpression.value = expression
}

const handleConfirm = () => {
  emit('confirm', cronExpression.value)
}

// 监听表达式变化，同步字段
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    parseExpressionToFields(newValue)
  }
}, { immediate: true })
</script>

<style lang="scss" scoped>
.cron-selector {
  .cron-preview {
    padding: 15px;
    background-color: #f5f7fa;
    border-radius: 4px;
    margin-bottom: 20px;

    h4 {
      margin: 0 0 8px 0;
      color: #303133;
      font-size: 16px;

      code {
        background-color: #e4e7ed;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: monospace;
        font-size: 14px;
      }
    }

    .preview-text {
      margin: 0;
      color: #409eff;
      font-size: 14px;
    }
  }

  .cron-tabs {
    :deep(.el-tabs__header) {
      margin-bottom: 20px;
    }

    :deep(.el-tabs__content) {
      padding: 0;
    }
  }

  .preset-list {
    .preset-group {
      margin-bottom: 24px;

      h5 {
        margin: 0 0 12px 0;
        color: #606266;
        font-size: 14px;
        font-weight: 600;
      }

      .preset-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }
    }
  }

  .custom-config {
    .field-group {
      margin-bottom: 15px;

      label {
        display: block;
        margin-bottom: 5px;
        font-weight: 500;
        color: #606266;
        font-size: 14px;
      }
    }

    .custom-help {
      margin-top: 20px;
      padding: 15px;
      background-color: #f5f7fa;
      border-radius: 4px;
      font-size: 13px;

      p {
        margin: 0 0 8px 0;
        font-weight: 600;
      }

      ul {
        margin: 0 0 12px 0;
        padding-left: 20px;

        li {
          margin-bottom: 4px;

          code {
            background-color: #e4e7ed;
            padding: 1px 4px;
            border-radius: 2px;
            font-family: monospace;
            font-size: 12px;
          }
        }
      }
    }
  }

  .cron-actions {
    margin-top: 24px;
    text-align: right;

    .el-button {
      margin-left: 10px;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .cron-selector {
    .preset-list {
      .preset-group {
        .preset-buttons {
          flex-direction: column;

          .el-button {
            width: 100%;
            margin-bottom: 5px;
          }
        }
      }
    }

    .custom-config {
      .el-row {
        .el-col {
          margin-bottom: 15px;
        }
      }
    }
  }
}
</style>
