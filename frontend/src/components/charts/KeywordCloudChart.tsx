import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import 'echarts-wordcloud';
import { KeywordCloud } from '../../utils/api';

interface Props {
  keywords: KeywordCloud[];
}

export default function KeywordCloudChart({ keywords }: Props) {
  const chartRef = useRef<HTMLDivElement>(null);
  const instanceRef = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;
    if (!instanceRef.current) {
      instanceRef.current = echarts.init(chartRef.current);
    }

    const maxCount = Math.max(...keywords.map((k) => k.count), 1);
    const minCount = Math.min(...keywords.map((k) => k.count), 1);

    const data = keywords.slice(0, 80).map((k) => ({
      name: k.word,
      value: k.count,
      textStyle: {
        color: `hsl(${140 + (k.count / maxCount) * 100}, 70%, ${40 + (k.count / maxCount) * 30}%)`,
      },
    }));

    instanceRef.current.setOption({
      backgroundColor: 'transparent',
      series: [{
        type: 'wordCloud',
        shape: 'circle',
        left: 'center',
        top: 'center',
        width: '90%',
        height: '90%',
        sizeRange: [12, 48],
        rotationRange: [-30, 30],
        rotationStep: 15,
        gridSize: 8,
        drawOutOfBound: false,
        layoutAnimation: true,
        textStyle: {
          fontFamily: 'Inter, sans-serif',
          color: '#e2e8f0',
        },
        data,
      }],
    }, true);

    const handleResize = () => instanceRef.current?.resize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [keywords]);

  return <div ref={chartRef} className="w-full h-64" />;
}
