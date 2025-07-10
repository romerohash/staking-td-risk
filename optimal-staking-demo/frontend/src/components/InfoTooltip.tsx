import React from 'react';
import { Tooltip, IconButton, Box, Typography, Link } from '@mui/material';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import { styled } from '@mui/material/styles';

interface InfoTooltipProps {
  title: string;
  description?: string;
  documentLink?: {
    path: string;
    title: string;
    section?: string;
  };
  onDocumentClick?: (path: string, title: string) => void;
  iconSize?: 'small' | 'medium';
  iconColor?: string;
}

const StyledTooltip = styled(({ className, ...props }: any) => (
  <Tooltip {...props} classes={{ popper: className }} />
))(({ theme }) => ({
  '& .MuiTooltip-tooltip': {
    backgroundColor: 'rgba(29, 41, 57, 0.98)',
    backdropFilter: 'blur(12px)',
    border: '1px solid rgba(109, 174, 255, 0.2)',
    borderRadius: '12px',
    padding: theme.spacing(1.5, 2),
    maxWidth: 320,
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
  },
  '& .MuiTooltip-arrow': {
    color: 'rgba(29, 41, 57, 0.98)',
    '&::before': {
      border: '1px solid rgba(109, 174, 255, 0.2)',
    },
  },
}));

export const InfoTooltip: React.FC<InfoTooltipProps> = ({
  title,
  description,
  documentLink,
  onDocumentClick,
  iconSize = 'small',
  iconColor = 'rgba(109, 174, 255, 0.5)',
}) => {
  const tooltipContent = (
    <Box>
      <Typography variant="body2" sx={{ color: '#D7E6FF', fontWeight: 500, mb: description || documentLink ? 1 : 0 }}>
        {title}
      </Typography>
      
      {description && (
        <Typography variant="caption" sx={{ color: 'rgba(215, 230, 255, 0.8)', display: 'block', mb: documentLink ? 1.5 : 0 }}>
          {description}
        </Typography>
      )}
      
      {documentLink && onDocumentClick && (
        <>
          <Box sx={{ borderTop: '1px solid rgba(109, 174, 255, 0.1)', pt: 1.5, mt: 1.5 }} />
          <Link
            component="button"
            variant="caption"
            onClick={(e) => {
              e.stopPropagation();
              const fullPath = documentLink.section 
                ? `${documentLink.path}#${documentLink.section}`
                : documentLink.path;
              onDocumentClick(fullPath, documentLink.title);
            }}
            sx={{
              color: '#6DAEFF',
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: 0.5,
              '&:hover': {
                color: '#8DC4FF',
                textDecoration: 'underline',
              },
            }}
          >
            Learn more → {documentLink.title}
          </Link>
        </>
      )}
    </Box>
  );

  return (
    <StyledTooltip
      title={tooltipContent}
      arrow
      placement="top"
      enterDelay={200}
      leaveDelay={100}
    >
      <IconButton
        size="small"
        sx={{
          p: 0,
          ml: 0.5,
          color: iconColor,
          '&:hover': {
            backgroundColor: 'transparent',
            color: '#6DAEFF',
          },
        }}
      >
        <InfoOutlinedIcon sx={{ fontSize: iconSize === 'small' ? 16 : 20 }} />
      </IconButton>
    </StyledTooltip>
  );
};