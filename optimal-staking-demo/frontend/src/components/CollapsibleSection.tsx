import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { Box, Collapse, IconButton, Typography } from "@mui/material";
import type React from "react";
import { useState } from "react";
import { glassStyles } from "../styles/glassmorphism";
import { GlassCard } from "./GlassCard";

interface CollapsibleSectionProps {
	title: string;
	children: React.ReactNode;
	defaultExpanded?: boolean;
	headerContent?: React.ReactNode;
	expanded?: boolean;
	onToggle?: () => void;
}

export const CollapsibleSection: React.FC<CollapsibleSectionProps> = ({
	title,
	children,
	defaultExpanded = true,
	headerContent,
	expanded: controlledExpanded,
	onToggle,
}) => {
	const [uncontrolledExpanded, setUncontrolledExpanded] =
		useState(defaultExpanded);

	const isControlled = controlledExpanded !== undefined;
	const expanded = isControlled ? controlledExpanded : uncontrolledExpanded;

	const handleToggle = () => {
		if (isControlled && onToggle) {
			onToggle();
		} else {
			setUncontrolledExpanded(!uncontrolledExpanded);
		}
	};

	return (
		<GlassCard hover={false}>
			<Box>
				<Box
					sx={{
						display: "flex",
						alignItems: "center",
						justifyContent: "space-between",
						p: 2,
						cursor: "pointer",
						transition: "background 0.2s ease",
						"&:hover": {
							background: "rgba(109, 174, 255, 0.05)",
						},
					}}
					onClick={handleToggle}
				>
					<Typography variant="h6" sx={glassStyles.gradientText}>
						{title}
					</Typography>
					{headerContent && (
						<Box
							sx={{
								marginLeft: "auto",
								marginRight: 2,
								display: "flex",
								alignItems: "center",
							}}
						>
							{headerContent}
						</Box>
					)}
					<IconButton
						size="small"
						sx={{
							color: "#6DAEFF",
							transition: "transform 0.2s ease",
						}}
					>
						{expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
					</IconButton>
				</Box>

				<Collapse in={expanded} timeout="auto" unmountOnExit>
					<Box sx={{ p: 3, pt: 0 }}>{children}</Box>
				</Collapse>
			</Box>
		</GlassCard>
	);
};
