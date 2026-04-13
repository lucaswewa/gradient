<template>
  <div ref="chartRef" style="width: 800px; height: 400px;"></div>
  <button @click="addMonth">Add Month</button>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'BarChart',
  data() {
    return {
      chartInstance: null,
      salesData: [
        { month: 'Jan', sales: 120 },
        { month: 'Feb', sales: 180 },
        { month: 'Mar', sales: 90 },
        { month: 'Apr', sales: 210 }
      ]
    }
  },
  watch: {
    salesData: {
      handler() {
        this.updateChart()
      },
      deep: true
    }
  },
  mounted() {
    this.initChart()
    window.addEventListener('resize', this.handleResize)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize)
    if (this.chartInstance) {
      this.chartInstance.dispose()
    }
  },
  methods: {
    initChart() {
      this.chartInstance = echarts.init(this.$refs.chartRef)
      this.chartInstance.setOption(this.getChartOptions())
    },
    updateChart() {
      if (this.chartInstance) {
        this.chartInstance.setOption({
          xAxis: {
            data: this.salesData.map(item => item.month)
          },
          series: [{
            data: this.salesData.map(item => item.sales)
          }]
        })
      }
    },
    addMonth() {
      const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
      const nextIndex = this.salesData.length
      if (nextIndex >= 12) return
      this.salesData.push({
        month: months[nextIndex],
        sales: Math.floor(Math.random() * 100) + 100
      })
    },
    getChartOptions() {
      return {
        title: {
          text: 'Monthly Sales Report',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: this.salesData.map(item => item.month)
        },
        yAxis: {
          type: 'value',
          name: 'Sales ($)'
        },
        series: [
          {
            name: 'Sales',
            type: 'bar',
            data: this.salesData.map(item => item.sales),
            itemStyle: {
              color: '#5470C6'
            }
          }
        ]
      }
    },
    handleResize() {
      if (this.chartInstance) {
        this.chartInstance.resize()
      }
    }
  }
}
</script>

<style scoped>
div {
  margin: 20px auto;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
</style>
