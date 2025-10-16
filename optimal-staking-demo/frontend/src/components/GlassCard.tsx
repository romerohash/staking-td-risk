import { Paper, type PaperProps } from "@mui/material";
import type React from "react";
import { glassStyles } from "../styles/glassmorphism";

interface GlassCardProps extends PaperProps {
	children: React.ReactNode;
	hover?: boolean;
}

export const GlassCard: React.FC<GlassCardProps> = ({
	children,
	sx,
	hover = true,
	...props
}) => {
	return (
		<Paper
			sx={{
				...(hover
					? glassStyles.card
					: {
							...glassStyles.card,
							"&:hover": {
								transform: "none",
								boxShadow: glassStyles.card.boxShadow,
								border: glassStyles.card.border,
							},
						}),
				...sx,
			}}
			elevation={0}
			{...props}
		>
			{children}
		</Paper>
	);
};
