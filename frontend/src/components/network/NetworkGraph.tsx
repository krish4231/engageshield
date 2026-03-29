import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

interface Props {
  graphData: {
    nodes: Array<{ id: string; label?: string; suspicion_score?: number; metrics?: any }>;
    edges: Array<{ source: string; target: string; weight: number }>;
  };
}

export default function NetworkGraph({ graphData }: Props) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current || !graphData?.nodes?.length) return;

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current, 'dark');
    }

    const chart = chartInstance.current;

    const nodes = graphData.nodes.map((node) => {
      const score = node.suspicion_score || 0;
      let color = '#10b981';
      let size = 12;

      if (score >= 0.7) {
        color = '#f43f5e';
        size = 22;
      } else if (score >= 0.4) {
        color = '#f59e0b';
        size = 17;
      } else if (score >= 0.2) {
        color = '#6366f1';
        size = 14;
      }

      return {
        name: node.id,
        symbolSize: size,
        itemStyle: { color, borderColor: 'rgba(255,255,255,0.1)', borderWidth: 1 },
        label: { show: size > 18, fontSize: 9, color: '#f1f5f9' },
      };
    });

    const edges = graphData.edges.map((edge) => ({
      source: edge.source,
      target: edge.target,
      lineStyle: {
        width: Math.min(edge.weight * 0.5, 4),
        color: 'rgba(99, 102, 241, 0.2)',
        curveness: 0.2,
      },
    }));

    chart.setOption({
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        backgroundColor: '#1a2035',
        borderColor: 'rgba(99,102,241,0.2)',
        textStyle: { color: '#f1f5f9', fontSize: 12 },
        formatter: (params: any) => {
          if (params.dataType === 'node') {
            const node = graphData.nodes.find((n) => n.id === params.name);
            const score = node?.suspicion_score || 0;
            return `<b>${params.name}</b><br/>Suspicion: ${(score * 100).toFixed(0)}%`;
          }
          return `${params.data.source} → ${params.data.target}`;
        },
      },
      series: [{
        type: 'graph',
        layout: 'force',
        data: nodes,
        links: edges,
        roam: true,
        force: {
          repulsion: 150,
          edgeLength: [50, 200],
          gravity: 0.05,
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: { width: 3 },
        },
      }],
    });

    const handleResize = () => chart.resize();
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [graphData]);

  return (
    <div className="chart-card">
      <div className="chart-card__header">
        <h3 className="chart-card__title">Engagement Network Graph</h3>
        <div className="flex gap-md" style={{ fontSize: '0.7rem' }}>
          <span style={{ color: '#10b981' }}>● Safe</span>
          <span style={{ color: '#f59e0b' }}>● Suspicious</span>
          <span style={{ color: '#f43f5e' }}>● Malicious</span>
        </div>
      </div>
      <div ref={chartRef} className="network-container" />
    </div>
  );
}
