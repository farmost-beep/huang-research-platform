import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import { TopicEvolution } from '../../utils/api';

interface Props {
  data: TopicEvolution[];
}

export default function RiverChart({ data }: Props) {
  const chartRef = useRef<HTMLDivElement>(null);
  const instanceRef = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current || data.length === 0) return;
    if (!instanceRef.current) {
      instanceRef.current = echarts.init(chartRef.current);
    }

    // 按主题分组
    const topicSet = new Set(data.map((d) => d.topic));
    const topics = Array.from(topicSet).slice(0, 8);

    // 按时间段聚合
    const periodMap = new Map<string, Record<string, number>>();
    data.forEach((d) => {
      if (!topics.includes(d.topic)) return;
      if (!periodMap.has(d.period)) periodMap.set(d.period, {});
      periodMap.get(d.period)![d.topic] = (periodMap.get(d.period)![d.topic] || 0) + d.intensity;
    });

    const periods = Array.from(periodMap.keys()).sort();

    const colors = ['#00d4aa', '#60a5fa', '#a78bfa', '#f472b6', '#fbbf24', '#34d399', '#f87171', '#2dd4bf'];

    const series = topics.map((topic, i) => ({
      type: 'themeRiver',
      name: topic,
      color: colors[i % colors.length],
      label: { show: false },
      data: periods.map((period) => [
        period,
        periodMap.get(period)?.[topic] || 0,
        topic,
      ]),
    }));

    instanceRef.current.setOption({
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'line' },
      },
      legend: {
        data: topics,
        textStyle: { color: '#9ca3af', fontSize: 11 },
        bottom: 0,
      },
      singleAxis: {
        type: 'time',
        axisLine: { lineStyle: { color: '#374151' } },
        axisLabel: { color: '#6b7280', fontSize: 10 },
        splitLine: { show: false },
      },
      series,
    }, true);

    const handleResize = () => instanceRef.current?.resize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [data]);

  if (data.length === 0) {
    return <div className="flex items-center justify-center h-64 text-gray-500 text-sm">暂无主题演化数据</div>;
  }

  return <div ref={chartRef} className="w-full h-64" />;
}
