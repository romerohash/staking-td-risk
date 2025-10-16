export const glassStyles = {
	card: {
		background: "rgba(255, 255, 255, 0.05)",
		backdropFilter: "blur(10px)",
		WebkitBackdropFilter: "blur(10px)",
		border: "1px solid rgba(109, 174, 255, 0.15)",
		borderRadius: "16px",
		boxShadow: "0 8px 32px 0 rgba(29, 41, 57, 0.37)",
		transition: "all 0.3s ease",
		"&:hover": {
			transform: "translateY(-2px)",
			boxShadow: "0 12px 40px 0 rgba(29, 41, 57, 0.45)",
			border: "1px solid rgba(109, 174, 255, 0.2)",
		},
	},
	input: {
		"& .MuiOutlinedInput-root": {
			background: "rgba(255, 255, 255, 0.05)",
			backdropFilter: "blur(5px)",
			WebkitBackdropFilter: "blur(5px)",
			borderRadius: "8px",
			"& fieldset": {
				borderColor: "rgba(255, 255, 255, 0.1)",
			},
			"&:hover fieldset": {
				borderColor: "rgba(255, 255, 255, 0.2)",
			},
			"&.Mui-focused fieldset": {
				borderColor: "#6DAEFF",
			},
		},
		"& .MuiInputLabel-root": {
			color: "rgba(255, 255, 255, 0.7)",
		},
		"& .MuiInputLabel-root.Mui-focused": {
			color: "#8DC4FF",
		},
	},
	button: {
		background: "linear-gradient(135deg, #6DAEFF 0%, #4A94E6 100%)",
		backdropFilter: "blur(10px)",
		WebkitBackdropFilter: "blur(10px)",
		border: "1px solid rgba(255, 255, 255, 0.1)",
		color: "#FFFFFF",
		transition: "all 0.3s ease",
		"&:hover": {
			transform: "translateY(-1px)",
			boxShadow: "0 4px 20px 0 rgba(109, 174, 255, 0.4)",
			background: "linear-gradient(135deg, #4A94E6 0%, #6DAEFF 100%)",
		},
		"&:active": {
			transform: "translateY(0)",
		},
	},
	buttonSubtle: {
		background: "rgba(109, 174, 255, 0.15)",
		backdropFilter: "blur(10px)",
		WebkitBackdropFilter: "blur(10px)",
		border: "1px solid rgba(109, 174, 255, 0.3)",
		color: "#FFFFFF",
		transition: "all 0.3s ease",
		"&:hover": {
			transform: "translateY(-1px)",
			boxShadow: "0 4px 20px 0 rgba(109, 174, 255, 0.2)",
			background: "rgba(109, 174, 255, 0.2)",
			border: "1px solid rgba(109, 174, 255, 0.4)",
		},
		"&:active": {
			transform: "translateY(0)",
		},
	},
	gradientText: {
		background: "linear-gradient(135deg, #6DAEFF 0%, #4A94E6 100%)",
		WebkitBackgroundClip: "text",
		WebkitTextFillColor: "transparent",
		backgroundClip: "text",
		textFillColor: "transparent",
	},
	chartTooltip: {
		background: "rgba(0, 0, 0, 0.8)",
		backdropFilter: "blur(10px)",
		WebkitBackdropFilter: "blur(10px)",
		border: "1px solid rgba(255, 255, 255, 0.2)",
		borderRadius: "8px",
		padding: "8px 12px",
	},
	statCard: {
		background: "rgba(109, 174, 255, 0.1)",
		backdropFilter: "blur(10px)",
		WebkitBackdropFilter: "blur(10px)",
		border: "1px solid rgba(109, 174, 255, 0.2)",
		borderRadius: "12px",
		padding: "16px",
		transition: "all 0.3s ease",
		"&:hover": {
			background: "rgba(109, 174, 255, 0.15)",
			border: "1px solid rgba(109, 174, 255, 0.3)",
			transform: "translateY(-1px)",
		},
	},
	backgroundGradient: {
		position: "fixed",
		width: "100%",
		height: "100%",
		top: 0,
		left: 0,
		background:
			"linear-gradient(135deg, #1D2939 0%, #161618 50%, #1D2939 100%)",
		zIndex: -1,
		"&::before": {
			content: '""',
			position: "absolute",
			width: "100%",
			height: "100%",
			background:
				"radial-gradient(circle at 20% 50%, rgba(109, 174, 255, 0.15) 0%, transparent 50%)",
		},
		"&::after": {
			content: '""',
			position: "absolute",
			width: "100%",
			height: "100%",
			background:
				"radial-gradient(circle at 80% 50%, rgba(109, 174, 255, 0.08) 0%, transparent 50%)",
		},
	},
};
