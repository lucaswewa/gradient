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
      ],
      dataAll: [
        [
          [10.0, 8.04],
          [8.0, 6.95],
          [13.0, 7.58],
          [9.0, 8.81],
          [11.0, 8.33],
          [14.0, 9.96],
          [6.0, 7.24],
          [4.0, 4.26],
          [12.0, 10.84],
          [7.0, 4.82],
          [5.0, 5.68]
        ],
        [
          [10.0, 9.14],
          [8.0, 8.14],
          [13.0, 8.74],
          [9.0, 8.77],
          [11.0, 9.26],
          [14.0, 8.1],
          [6.0, 6.13],
          [4.0, 3.1],
          [12.0, 9.13],
          [7.0, 7.26],
          [5.0, 4.74]
        ],
        [
          [10.0, 7.46],
          [8.0, 6.77],
          [13.0, 12.74],
          [9.0, 7.11],
          [11.0, 7.81],
          [14.0, 8.84],
          [6.0, 6.08],
          [4.0, 5.39],
          [12.0, 8.15],
          [7.0, 6.42],
          [5.0, 5.73]
        ],
        [
          [8.0, 6.58],
          [8.0, 5.76],
          [8.0, 7.71],
          [8.0, 8.84],
          [8.0, 8.47],
          [8.0, 7.04],
          [8.0, 5.25],
          [19.0, 12.5],
          [8.0, 5.56],
          [8.0, 7.91],
          [8.0, 6.89]
        ]
      ],
      markLineOpt: {
        animation: false,
        label: {
          formatter: 'y = 0.5 * x + 3',
          align: 'right'
        },
        lineStyle: {
          type: 'solid'
        },
        tooltip: {
          formatter: 'y = 0.5 * x + 3'
        },
        data: [
          [
            {
              coord: [0, 3],
              symbol: 'none'
            },
            {
              coord: [20, 13],
              symbol: 'none'
            }
          ]
        ]
      },
    }
  },
  watch: {
    scatter_data: {
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
    func(x) {
      x /= 10;
      return Math.sin(x) * Math.cos(x * 2 + 1) * Math.sin(x * 3 + 2) * 40 + 15;
    },
    generateData() {
      let data = [];
      for (let i = 0; i <= 100; i += 0.1) {
        data.push([i, this.func(i)]);
      }
      return data;
    },
    getChartOptions() {
      return   {
        animation: false,
        grid: {
          top: 40,
          left: 50,
          right: 40,
          bottom: 50
        },
        xAxis: {
          name: 'x',
          minorTick: {
            show: true
          },
          minorSplitLine: {
            show: true
          }
        },
        yAxis: {
          name: 'y',
          min: 0,
          max: 100,
          minorTick: {
            show: true
          },
          minorSplitLine: {
            show: true
          }
        },
        dataZoom: [
          {
            show: true,
            type: 'inside',
            filterMode: 'none',
            xAxisIndex: [0],
            startValue: 0,
            endValue: 100
          },
          {
            show: true,
            type: 'inside',
            filterMode: 'none',
            yAxisIndex: [0],
            startValue: 0,
            endValue: 50
          }
        ],
        series: [
          {
            type: 'line',
            showSymbol: false,
            clip: true,
            data: this.generateData()
          }
        ]
      };
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
