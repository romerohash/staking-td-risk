import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Chip,
  Stack,
  TextField,
  InputAdornment,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import { RedemptionDistributionItem } from '../types';
import { glassStyles } from '../styles/glassmorphism';
import { InfoTooltip } from './InfoTooltip';

interface RedemptionDistributionBuilderProps {
  distribution: RedemptionDistributionItem[];
  onChange: (distribution: RedemptionDistributionItem[]) => void;
  expectedRedemptionsPerYear: number;
  onDocumentClick?: (path: string, title: string) => void;
}

export const RedemptionDistributionBuilder: React.FC<RedemptionDistributionBuilderProps> = ({
  distribution,
  onChange,
  expectedRedemptionsPerYear,
  onDocumentClick,
}) => {
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const chartRef = useRef<HTMLDivElement>(null);

  // Precise normalization function with two passes
  const normalizeProbabilities = useCallback((items: RedemptionDistributionItem[]): RedemptionDistributionItem[] => {
    if (items.length === 0) return items;
    
    // First pass: calculate total and normalize
    const total = items.reduce((sum, item) => sum + item.probability, 0);
    if (total === 0) return items;
    
    const normalized = items.map(item => ({
      ...item,
      probability: item.probability / total
    }));
    
    // Second pass: adjust last item to ensure exact sum of 1.0
    const normalizedSum = normalized.slice(0, -1).reduce((sum, item) => sum + item.probability, 0);
    normalized[normalized.length - 1].probability = 1.0 - normalizedSum;
    
    // Ensure last item is not negative due to rounding
    if (normalized[normalized.length - 1].probability < 0) {
      normalized[normalized.length - 1].probability = 0;
    }
    
    return normalized;
  }, []);

  // Prepare data for chart
  const chartData = distribution.map((item, index) => ({
    name: `${(item.size * 100).toFixed(0)}%`,
    probability: item.probability * 100,
    size: item.size * 100,
    index,
  }));

  // Colors for bars
  const barColors = ['#6DAEFF', '#4A94E6', '#357ABD', '#1E5A93', '#0A3A69'];

  // Handle mouse down on bar
  const handleBarMouseDown = (_data: any, index: number) => {
    setDraggedIndex(index);
  };

  // Handle mouse move
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (draggedIndex === null || !chartRef.current) return;

      const rect = chartRef.current.getBoundingClientRect();
      const chartHeight = rect.height - 100; // Account for margins
      const mouseY = e.clientY - rect.top;
      const relativeY = chartHeight - mouseY;
      const newProbability = Math.max(0, Math.min(100, (relativeY / chartHeight) * 100));

      const newDistribution = [...distribution];
      newDistribution[draggedIndex] = {
        ...newDistribution[draggedIndex],
        probability: newProbability / 100,
      };

      // Normalize probabilities with precision
      const normalized = normalizeProbabilities(newDistribution);
      onChange(normalized);
    };

    const handleMouseUp = () => {
      setDraggedIndex(null);
    };

    if (draggedIndex !== null) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [draggedIndex, distribution, onChange, normalizeProbabilities]);

  // Add new redemption size
  const addRedemptionSize = () => {
    const newItem: RedemptionDistributionItem = {
      probability: 0.1,
      size: 0.4,
    };
    const newDistribution = [...distribution, newItem];
    
    // Normalize with precision
    const normalized = normalizeProbabilities(newDistribution);
    onChange(normalized);
  };

  // Remove redemption size
  const removeRedemptionSize = (index: number) => {
    if (distribution.length <= 1) return;
    
    const newDistribution = distribution.filter((_, i) => i !== index);
    
    // Normalize with precision
    const normalized = normalizeProbabilities(newDistribution);
    onChange(normalized);
  };

  // Update size for a specific item
  const updateSize = (index: number, newSize: number) => {
    const newDistribution = [...distribution];
    newDistribution[index] = {
      ...newDistribution[index],
      size: newSize / 100,
    };
    onChange(newDistribution);
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload[0]) {
      return (
        <Box
          sx={{
            background: 'rgba(29, 41, 57, 0.95)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(109, 174, 255, 0.3)',
            borderRadius: 1,
            p: 1.5,
          }}
        >
          <Typography variant="body2" sx={{ color: '#6DAEFF', mb: 0.5 }}>
            Redemption Size: {payload[0].payload.name} of AUM
          </Typography>
          <Typography variant="body2" sx={{ color: '#D7E6FF' }}>
            Probability: {payload[0].value.toFixed(1)}%
          </Typography>
        </Box>
      );
    }
    return null;
  };

  return (
    <Stack spacing={3}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="subtitle2" color="text.secondary">
            Redemption Size Distribution
          </Typography>
          <InfoTooltip
            title="Drag the bars up or down to adjust probabilities. They will automatically normalize to 100%."
            documentLink={{
              path: 'analytical-tracking-error-formula.md',
              title: 'Redemption Size Distributions',
              section: 'redemption-size-distributions-and-er---τ₊'
            }}
            onDocumentClick={onDocumentClick}
          />
        </Box>
        <IconButton
          size="small"
          onClick={addRedemptionSize}
          sx={{ color: '#6DAEFF' }}
        >
          <AddIcon />
        </IconButton>
      </Box>

      {/* Interactive Bar Chart */}
      <Box
        ref={chartRef}
        sx={{
          width: '100%',
          height: 300,
          background: 'rgba(109, 174, 255, 0.02)',
          borderRadius: 2,
          border: '1px solid rgba(109, 174, 255, 0.1)',
          p: 2,
          cursor: draggedIndex !== null ? 'grabbing' : 'default',
        }}
      >
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{ top: 20, right: 20, bottom: 40, left: 20 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="rgba(109, 174, 255, 0.1)"
            />
            <XAxis
              dataKey="name"
              tick={{ fill: '#8FA0B5' }}
              label={{
                value: 'Redemption Size (% of AUM)',
                position: 'insideBottom',
                offset: -10,
                fill: '#8FA0B5',
              }}
            />
            <YAxis
              tick={{ fill: '#8FA0B5' }}
              label={{
                value: 'Probability (%)',
                angle: -90,
                position: 'insideLeft',
                offset: 10,
                style: { textAnchor: 'middle' },
                fill: '#8FA0B5',
              }}
              domain={[0, 100]}
            />
            <RechartsTooltip content={<CustomTooltip />} />
            <Bar
              dataKey="probability"
              radius={[8, 8, 0, 0]}
              onMouseDown={(data: any, index: number) => handleBarMouseDown(data, index)}
              onMouseEnter={(_data: any, index: number) => setHoveredIndex(index)}
              onMouseLeave={() => setHoveredIndex(null)}
              cursor="grab"
            >
              {chartData.map((_entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={barColors[index % barColors.length]}
                  style={{
                    filter: draggedIndex === index 
                      ? 'brightness(1.2)' 
                      : hoveredIndex === index 
                      ? 'brightness(1.05) opacity(0.85)' 
                      : 'none',
                    transition: 'filter 0.2s ease, opacity 0.2s ease',
                  }}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Box>

      {/* Size Inputs */}
      <Stack spacing={2}>
        <Typography variant="body2" color="text.secondary">
          Redemption Sizes:
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {distribution.map((item, index) => (
            <Box
              key={index}
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                background: 'rgba(109, 174, 255, 0.05)',
                borderRadius: 2,
                p: 1,
                border: '1px solid rgba(109, 174, 255, 0.1)',
              }}
            >
              <TextField
                size="small"
                type="number"
                value={(item.size * 100).toFixed(0)}
                onChange={(e) => updateSize(index, parseFloat(e.target.value) || 0)}
                InputProps={{
                  endAdornment: <InputAdornment position="end">%</InputAdornment>,
                }}
                sx={{
                  width: 87.5,
                  '& .MuiInputBase-input': {
                    color: '#D7E6FF',
                    fontSize: '0.875rem',
                  },
                  ...glassStyles.input,
                }}
              />
              <Chip
                label={`${(item.probability * 100).toFixed(1)}%`}
                size="small"
                sx={{
                  background: barColors[index % barColors.length],
                  color: '#ffffff',
                  fontWeight: 500,
                }}
              />
              {distribution.length > 1 && (
                <IconButton
                  size="small"
                  onClick={() => removeRedemptionSize(index)}
                  sx={{ color: 'rgba(255, 255, 255, 0.5)', p: 0.5 }}
                >
                  <RemoveIcon fontSize="small" />
                </IconButton>
              )}
            </Box>
          ))}
        </Box>
      </Stack>

      {/* Summary */}
      <Box
        sx={{
          background: 'rgba(109, 174, 255, 0.05)',
          borderRadius: 2,
          p: 2,
          border: '1px solid rgba(109, 174, 255, 0.1)',
        }}
      >
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          Distribution Summary:
        </Typography>
        <Stack spacing={0.5}>
          <Typography variant="caption" sx={{ color: '#D7E6FF' }}>
            • Total Probability: {(distribution.reduce((sum, item) => sum + item.probability, 0) * 100).toFixed(1)}% (auto-normalized)
          </Typography>
          <Typography variant="caption" sx={{ color: '#D7E6FF' }}>
            • Expected redemption: {(distribution.reduce((sum, item) => sum + item.probability * item.size, 0) * 100).toFixed(2)}% of AUM
          </Typography>
          <Typography variant="caption" sx={{ color: '#D7E6FF' }}>
            • Chance of occurring: {(expectedRedemptionsPerYear / 365 * 100).toFixed(2)}% daily
          </Typography>
        </Stack>
      </Box>
    </Stack>
  );
};