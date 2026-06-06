import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import { SentimentTrend } from '../../utils/api';

interface Props {
  data: SentimentTrend[];
}

export default function SentimentChart({ data }: Props) {
  const chartRef = useRef<HTMLDivElement>(null);
  const instanceRef = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current || data.length === 0) return;
    if (!instanceRef.current) {
      instanceRef.current = echarts.init(chartRef.current);
    }

    // 按标签分组
    const labels = [...new Set(data.map((d) => d.label))];
    const periods = [...new Set(data.map((d) => d.period))].sort();

    const series = labels.map((label) => ({
      name: label,
      type: 'line' as const,
      smooth: true,
      data: periods.map((p) => {
        const item = data.find((d) => d.period === p && d.label === label);
        return item?.count || 0;
      }),
    }));

    const colorMap: Record<string, string> = {
      positive: '#34d399',
      excited: '#00d4aa',
      neutral: '#9ca3af',
      negative: '#f87171',
      cautious: '#fbbf24',
    };

    instanceRef.current.setOption({
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        backgroundColor: '#1a1a2e',
        borderColor: '#374151',
        textStyle: { color: '#e5e7eb' },
      },
      legend: {
        data: labels,
        textStyle: { color: '#9ca3af', fontSize: 11 },
        top: 0,
      },
      grid: {
        top: 40,
        left: 40,
        right: 20,
        bottom: 30,
      },
      xAxis: {
        type: 'category',
        data: periods,
        axisLine: { lineStyle: { color: '#374151' } },
        axisLabel: { color: '#6b7280', fontSize: 10, rotate: 45 },
        splitLine: { show: false },
      },
      yAxis: {
        type: 'value',
        axisLine: { show: false },
        axisLabel: { color: '#6b7280', fontSize: 10 },
        splitLine: { lineStyle: { color: '#1f2937' } },
      },
      series: series.map((s) => ({
        ...s,
        color: colorMap[s.name] || '#60a5fa',
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: (colorMap[s.name] || '#60a5fa') + '40' },
            { offset: 1, color: (colorMap[s.name] || '#60a5fa') + '05' },
          ]),
        },
        lineStyle: { width: 2 },
        symbol: 'circle',
        symbolSize: 4,
      })),
    }, true);

    const handleResize = () => instanceRef.current?.resize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [data]);

  if (data.length === 0) {
    return <div className="flex items-center justify-center h-48 text-gray-500 text-sm">暂无情感数据</div>;
  }

  return <div ref={chartRef} className="w-full h-48" />;
}
