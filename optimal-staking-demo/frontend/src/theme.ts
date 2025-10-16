import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
	palette: {
		mode: "dark",
		primary: {
			main: "#6DAEFF",
			light: "#8DC4FF",
			dark: "#4A94E6",
		},
		secondary: {
			main: "#6DAEFF",
			light: "#8DC4FF",
			dark: "#4A94E6",
		},
		background: {
			default: "#1D2939",
			paper: "rgba(255, 255, 255, 0.05)",
		},
		text: {
			primary: "#FFFFFF",
			secondary: "rgba(255, 255, 255, 0.7)",
		},
	},
	typography: {
		fontFamily: '"Inter", "Helvetica", "Arial", sans-serif',
		h1: {
			fontSize: "3rem",
			fontWeight: 700,
			letterSpacing: "-0.02em",
		},
		h2: {
			fontSize: "2.25rem",
			fontWeight: 600,
			letterSpacing: "-0.01em",
		},
		h3: {
			fontSize: "1.875rem",
			fontWeight: 600,
		},
		h4: {
			fontSize: "1.5rem",
			fontWeight: 600,
		},
		h5: {
			fontSize: "1.25rem",
			fontWeight: 500,
		},
		h6: {
			fontSize: "1rem",
			fontWeight: 500,
		},
	},
	shape: {
		borderRadius: 16,
	},
	components: {
		MuiPaper: {
			styleOverrides: {
				root: {
					backgroundImage: "none",
				},
			},
		},
		MuiButton: {
			styleOverrides: {
				root: {
					textTransform: "none",
					fontWeight: 500,
					borderRadius: 8,
				},
			},
		},
		MuiTextField: {
			styleOverrides: {
				root: {
					"& .MuiOutlinedInput-root": {
						borderRadius: 8,
					},
				},
			},
		},
	},
});
