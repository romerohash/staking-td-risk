import CloseIcon from "@mui/icons-material/Close";
import {
	Box,
	CircularProgress,
	Dialog,
	DialogContent,
	DialogTitle,
	IconButton,
	Typography,
} from "@mui/material";
import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import rehypeKatex from "rehype-katex";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import { glassStyles } from "../styles/glassmorphism";
import "katex/dist/katex.min.css";

interface MarkdownViewerProps {
	open: boolean;
	onClose: () => void;
	documentPath: string | null;
	documentTitle: string;
}

// Cache for storing fetched documents
const documentCache = new Map<string, string>();

export function MarkdownViewer({
	open,
	onClose,
	documentPath,
	documentTitle,
}: MarkdownViewerProps) {
	const [content, setContent] = useState<string>("");
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		if (open && documentPath) {
			fetchDocument(documentPath);
		}
	}, [open, documentPath, fetchDocument]);

	const fetchDocument = async (path: string) => {
		setLoading(true);
		setError(null);

		// Check cache first
		if (documentCache.has(path)) {
			setContent(documentCache.get(path)!);
			setLoading(false);
			return;
		}

		try {
			const response = await fetch(`/api/docs/${path}`);
			if (!response.ok) {
				throw new Error(`Failed to fetch document: ${response.statusText}`);
			}
			const text = await response.text();

			// Cache the document
			documentCache.set(path, text);
			setContent(text);
		} catch (err) {
			setError(err instanceof Error ? err.message : "Failed to load document");
		} finally {
			setLoading(false);
		}
	};

	return (
		<Dialog
			open={open}
			onClose={onClose}
			maxWidth="lg"
			fullWidth
			PaperProps={{
				sx: {
					background: "rgba(29, 41, 57, 0.95)",
					backdropFilter: "blur(20px)",
					WebkitBackdropFilter: "blur(20px)",
					border: "1px solid rgba(109, 174, 255, 0.2)",
					borderRadius: "16px",
					boxShadow: "0 8px 32px 0 rgba(29, 41, 57, 0.37)",
					maxHeight: "90vh",
				},
			}}
		>
			<DialogTitle
				sx={{
					display: "flex",
					alignItems: "center",
					justifyContent: "space-between",
					borderBottom: "1px solid rgba(109, 174, 255, 0.15)",
					pb: 2,
				}}
			>
				<Typography variant="h5" sx={glassStyles.gradientText}>
					{documentTitle}
				</Typography>
				<IconButton
					onClick={onClose}
					sx={{
						color: "rgba(255, 255, 255, 0.7)",
						"&:hover": {
							background: "rgba(109, 174, 255, 0.1)",
						},
					}}
				>
					<CloseIcon />
				</IconButton>
			</DialogTitle>
			<DialogContent
				sx={{
					mt: 2,
					"& .markdown-content": {
						color: "rgba(255, 255, 255, 0.9)",
						"& h1, & h2, & h3, & h4, & h5, & h6": {
							...glassStyles.gradientText,
							mt: 3,
							mb: 2,
						},
						"& h1": { fontSize: "2rem", fontWeight: 700 },
						"& h2": { fontSize: "1.5rem", fontWeight: 600 },
						"& h3": { fontSize: "1.25rem", fontWeight: 600 },
						"& p": {
							mb: 2,
							lineHeight: 1.7,
							color: "rgba(255, 255, 255, 0.85)",
						},
						"& code": {
							background: "rgba(109, 174, 255, 0.1)",
							padding: "2px 6px",
							borderRadius: "4px",
							fontFamily: "monospace",
							fontSize: "0.9em",
							color: "#8DC4FF",
						},
						"& pre": {
							background: "rgba(0, 0, 0, 0.3)",
							padding: "16px",
							borderRadius: "8px",
							overflow: "auto",
							mb: 2,
							border: "1px solid rgba(109, 174, 255, 0.2)",
							"& code": {
								background: "none",
								padding: 0,
								color: "rgba(255, 255, 255, 0.9)",
							},
						},
						"& blockquote": {
							borderLeft: "4px solid #6DAEFF",
							pl: 2,
							ml: 0,
							mr: 0,
							color: "rgba(255, 255, 255, 0.8)",
							fontStyle: "italic",
						},
						"& ul, & ol": {
							mb: 2,
							pl: 3,
							"& li": {
								mb: 1,
								color: "rgba(255, 255, 255, 0.85)",
							},
						},
						"& table": {
							width: "100%",
							borderCollapse: "collapse",
							mb: 2,
							"& th, & td": {
								border: "1px solid rgba(109, 174, 255, 0.2)",
								padding: "8px 12px",
								textAlign: "left",
							},
							"& th": {
								background: "rgba(109, 174, 255, 0.1)",
								fontWeight: 600,
								color: "#8DC4FF",
							},
							"& tr:hover": {
								background: "rgba(109, 174, 255, 0.05)",
							},
						},
						"& a": {
							color: "#8DC4FF",
							textDecoration: "none",
							"&:hover": {
								textDecoration: "underline",
							},
						},
						"& hr": {
							border: "none",
							borderTop: "1px solid rgba(109, 174, 255, 0.2)",
							my: 3,
						},
						// KaTeX math styling
						"& .katex": {
							fontSize: "1.1em",
						},
						"& .katex-display": {
							margin: "1em 0",
							overflow: "auto",
						},
					},
				}}
			>
				{loading && (
					<Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
						<CircularProgress sx={{ color: "#6DAEFF" }} />
					</Box>
				)}
				{error && (
					<Box
						sx={{
							...glassStyles.card,
							background: "rgba(239, 68, 68, 0.1)",
							border: "1px solid rgba(239, 68, 68, 0.3)",
							p: 2,
							textAlign: "center",
						}}
					>
						<Typography color="error">{error}</Typography>
					</Box>
				)}
				{!loading && !error && content && (
					<Box className="markdown-content">
						<ReactMarkdown
							remarkPlugins={[remarkGfm, remarkMath]}
							rehypePlugins={[rehypeKatex]}
						>
							{content}
						</ReactMarkdown>
					</Box>
				)}
			</DialogContent>
		</Dialog>
	);
}
