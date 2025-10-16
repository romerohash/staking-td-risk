import TrendingDownIcon from "@mui/icons-material/TrendingDown";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import {
	Box,
	Grid,
	LinearProgress,
	Stack,
	Table,
	TableBody,
	TableCell,
	TableContainer,
	TableHead,
	TableRow,
	Typography,
} from "@mui/material";
import type React from "react";
import Plot from "react-plotly.js";
import { glassStyles } from "../styles/glassmorphism";
import type { CalculationResponse } from "../types";
import { GlassCard } from "./GlassCard";
import { InfoTooltip } from "./InfoTooltip";

interface ResultsDisplayProps {
	results: CalculationResponse | null;
	loading: boolean;
	autoCalculate: boolean;
	onDocumentClick?: (path: string, title: string) => void;
}

export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({
	results,
	loading,
	autoCalculate,
	onDocumentClick,
}) => {
	// Helper function to format currency
	const formatCurrency = (value: number): string => {
		return new Intl.NumberFormat("en-US", {
			style: "currency",
			currency: "USD",
			minimumFractionDigits: 0,
			maximumFractionDigits: 0,
		}).format(value);
	};

	// Helper function to calculate dollar value
	const calculateDollarValue = (percentage: number): number => {
		const nav = results?.parameters_used?.fund_details?.nav || 0;
		return nav * percentage;
	};
	// Only show loading animation when Auto toggle is disabled
	if (loading && !autoCalculate) {
		return (
			<GlassCard>
				<Box p={4}>
					<Typography variant="h6" sx={{ mb: 2 }}>
						Calculating...
					</Typography>
					<LinearProgress
						sx={{
							background: "rgba(109, 174, 255, 0.1)",
							"& .MuiLinearProgress-bar": {
								background: "linear-gradient(90deg, #6DAEFF 0%, #4A94E6 100%)",
							},
						}}
					/>
				</Box>
			</GlassCard>
		);
	}

	if (!results) {
		return (
			<GlassCard>
				<Box p={4} textAlign="center">
					<Typography variant="h6" color="text.secondary">
						Calculate to see results
					</Typography>
				</Box>
			</GlassCard>
		);
	}

	// Prepare 3D surface data
	const prepare3DSurfaceData = () => {
		if (!results.sensitivity_analysis_2d) {
			return {
				ethLevels: [],
				solLevels: [],
				teValues: [],
				netBenefitValues: [],
			};
		}

		// Get unique ETH and SOL levels
		const ethLevels = [
			...new Set(
				results.sensitivity_analysis_2d.map((p) => p.eth_staking_level),
			),
		].sort();
		const solLevels = [
			...new Set(
				results.sensitivity_analysis_2d.map((p) => p.sol_staking_level),
			),
		].sort();

		// Create 2D arrays for TE and Net Benefit
		const teValues: number[][] = [];
		const netBenefitValues: number[][] = [];

		for (const ethLevel of ethLevels) {
			const teRow: number[] = [];
			const netBenefitRow: number[] = [];

			for (const solLevel of solLevels) {
				const point = results.sensitivity_analysis_2d.find(
					(p) =>
						p.eth_staking_level === ethLevel &&
						p.sol_staking_level === solLevel,
				);
				if (point) {
					teRow.push(point.tracking_error * 100);
					netBenefitRow.push(point.net_benefit_bps / 100);
				} else {
					teRow.push(0);
					netBenefitRow.push(0);
				}
			}

			teValues.push(teRow);
			netBenefitValues.push(netBenefitRow);
		}

		return {
			ethLevels: ethLevels.map((l) => l * 100),
			solLevels: solLevels.map((l) => l * 100),
			teValues,
			netBenefitValues,
		};
	};

	const { ethLevels, solLevels, teValues, netBenefitValues } =
		prepare3DSurfaceData();

	return (
		<Stack spacing={3}>
			{/* Main Results */}
			<GlassCard>
				<Box p={2}>
					<Typography
						variant="h5"
						sx={{ mb: 1.5, ...glassStyles.gradientText }}
					>
						Main Results
					</Typography>

					<Grid container spacing={1.5}>
						{/* Card 1: User Input Results */}
						<Grid item xs={12} lg={6}>
							<Box sx={{ ...glassStyles.statCard, p: 2, height: "100%" }}>
								<Typography
									variant="h6"
									sx={{ mb: 1.5, fontWeight: 600, color: "#6DAEFF" }}
								>
									Performance Metrics
								</Typography>
								<Grid container spacing={2}>
									{/* First row */}
									<Grid item xs={12} sm={4}>
										<Box>
											<Typography
												variant="body2"
												color="text.secondary"
												sx={{ mb: 0.5 }}
											>
												Annual Tracking Error
											</Typography>
											<Box
												sx={{ display: "flex", alignItems: "baseline", gap: 1 }}
											>
												<Typography variant="h5" fontWeight={600}>
													{(results.decomposition.tracking_error * 100).toFixed(
														3,
													)}
													%
												</Typography>
												<InfoTooltip
													title="Standard deviation of portfolio returns vs benchmark"
													documentLink={{
														path: "analytical-tracking-error-formula.md",
														title: "Analytical Tracking Error Formula",
													}}
													onDocumentClick={onDocumentClick}
												/>
											</Box>
										</Box>
									</Grid>
									<Grid item xs={12} sm={4}>
										<Box>
											<Typography
												variant="body2"
												color="text.secondary"
												sx={{ mb: 0.5 }}
											>
												Expected Shortfall
											</Typography>
											<Box
												sx={{ display: "flex", alignItems: "baseline", gap: 1 }}
											>
												<Typography variant="h5" fontWeight={600} color="error">
													{(
														results.net_benefit.expected_shortfall * 100
													).toFixed(3)}
													%
												</Typography>
												<InfoTooltip
													title="Expected tracking error cost (tracking difference proxy)"
													description="Approximated as TE × √(2/π) × 0.5, representing the expected tracking error when it is negative (under normal distribution assumptions)"
													documentLink={{
														path: "staking-benefit-formulation.md",
														title: "Staking Benefit Formulation",
														section: "net-benefit-analysis",
													}}
													onDocumentClick={onDocumentClick}
												/>
											</Box>
										</Box>
									</Grid>
									<Grid item xs={12} sm={4}>
										<Box>
											<Typography
												variant="body2"
												color="text.secondary"
												sx={{ mb: 0.5 }}
											>
												TD Budget Deficit
											</Typography>
											<Box
												sx={{ display: "flex", alignItems: "baseline", gap: 1 }}
											>
												<Typography
													variant="h5"
													fontWeight={600}
													sx={{
														color:
															results.net_benefit.td_budget_deficit < 0
																? "#EF4444"
																: "#10B981",
													}}
												>
													{(
														results.net_benefit.td_budget_deficit * 10000
													).toFixed(1)}{" "}
													bps
												</Typography>
												<InfoTooltip
													title="TD budget deficit"
													description="MIN[0, (TD Budget - |Expected Shortfall|)]. Note: Expected Shortfall is already negative, so we use its absolute value. Negative deficit values indicate the TD budget is exceeded."
													onDocumentClick={onDocumentClick}
												/>
											</Box>
										</Box>
									</Grid>

									{/* Second row */}
									<Grid item xs={12} sm={4}>
										<Box>
											<Typography
												variant="body2"
												color="text.secondary"
												sx={{ mb: 0.5 }}
											>
												Total Yield
											</Typography>
											<Box
												sx={{ display: "flex", alignItems: "baseline", gap: 1 }}
											>
												<Typography
													variant="h5"
													fontWeight={600}
													sx={{ color: "#10B981" }}
												>
													{(
														results.net_benefit.total_yield_benefit * 100
													).toFixed(3)}
													%
												</Typography>
												<InfoTooltip
													title="Combined staking yield from ETH and SOL"
													description="Includes baseline benefits (staking above 70%) plus marginal overweight benefits during redemption episodes"
													documentLink={{
														path: "staking-benefit-formulation.md",
														title: "Staking Benefit Formulation",
														section: "the-two-components-of-staking-benefit",
													}}
													onDocumentClick={onDocumentClick}
												/>
											</Box>
										</Box>
									</Grid>
									<Grid item xs={12} sm={4}>
										<Box>
											<Typography
												variant="body2"
												color="text.secondary"
												sx={{ mb: 0.5 }}
											>
												TD Budget
											</Typography>
											<Box
												sx={{ display: "flex", alignItems: "baseline", gap: 1 }}
											>
												<Typography
													variant="h5"
													fontWeight={600}
													sx={{ color: "#3B82F6" }}
												>
													{(
														results.net_benefit.tracking_difference_budget *
														10000
													).toFixed(1)}{" "}
													bps
												</Typography>
												<InfoTooltip
													title="Available TD budget (Cap TD - Current TD)"
													description="The tracking difference budget available for staking activities"
													onDocumentClick={onDocumentClick}
												/>
											</Box>
										</Box>
									</Grid>
									<Grid item xs={12} sm={4}>
										<Box>
											<Typography
												variant="body2"
												color="text.secondary"
												sx={{ mb: 0.5 }}
											>
												Net Benefit
											</Typography>
											<Box
												sx={{ display: "flex", alignItems: "baseline", gap: 1 }}
											>
												<Typography
													variant="h5"
													fontWeight={600}
													sx={glassStyles.gradientText}
												>
													{results.net_benefit.net_benefit_bps.toFixed(1)} bps
												</Typography>
												{results.net_benefit.net_benefit_bps > 0 && (
													<TrendingUpIcon
														sx={{ fontSize: 16, color: "#10B981" }}
													/>
												)}
												{results.net_benefit.net_benefit_bps < 0 && (
													<TrendingDownIcon
														sx={{ fontSize: 16, color: "#EF4444" }}
													/>
												)}
												<InfoTooltip
													title="Net Benefit = Total Yield + TD Budget Deficit"
													description="The final metric that determines optimal staking levels. Since TD Budget Deficit is non-positive, adding it reduces the Net Benefit when there is a deficit"
													documentLink={{
														path: "staking-benefit-formulation.md",
														title: "Staking Benefit Formulation",
														section: "net-benefit-analysis",
													}}
													onDocumentClick={onDocumentClick}
												/>
											</Box>
										</Box>
									</Grid>
								</Grid>
							</Box>
						</Grid>

						{/* Card 2: Optimal Staking Levels */}
						<Grid item xs={12} lg={6}>
							<Box sx={{ ...glassStyles.statCard, p: 2, height: "100%" }}>
								<Typography
									variant="h6"
									sx={{ mb: 1.5, fontWeight: 600, color: "#10B981" }}
								>
									Optimal Staking Levels
								</Typography>
								<Box
									sx={{
										display: "flex",
										alignItems: "center",
										gap: 1,
										mb: 0.5,
									}}
								>
									<Typography variant="body2" color="text.secondary">
										Staking levels that maximize net benefit
									</Typography>
									<InfoTooltip
										title="Optimal staking levels"
										description="The combination of ETH and SOL staking percentages that maximizes net benefit by balancing yield opportunities against liquidity risks"
										documentLink={{
											path: "staking-benefit-formulation.md",
											title: "Staking Benefit Formulation",
										}}
										onDocumentClick={onDocumentClick}
									/>
								</Box>
								<Grid container spacing={2} sx={{ mt: 0 }}>
									<Grid item xs={6}>
										<Box sx={{ textAlign: "center" }}>
											<Box
												sx={{
													width: 80,
													height: 80,
													mx: "auto",
													mb: 1,
													borderRadius: "50%",
													background:
														"linear-gradient(135deg, #6DAEFF 0%, #4A94E6 100%)",
													display: "flex",
													alignItems: "center",
													justifyContent: "center",
													boxShadow: "0 4px 20px rgba(109, 174, 255, 0.3)",
												}}
											>
												<Box>
													<Typography
														variant="h5"
														fontWeight={700}
														color="white"
													>
														{Math.round(
															results.optimal_staking_levels.eth * 100,
														)}
														%
													</Typography>
													<Typography
														variant="caption"
														color="white"
														fontWeight={500}
														sx={{ fontSize: "0.7rem" }}
													>
														ETH
													</Typography>
												</Box>
											</Box>
											<Typography
												variant="caption"
												color="text.secondary"
												sx={{ fontSize: "0.75rem" }}
											>
												Ethereum Optimal Level
											</Typography>
										</Box>
									</Grid>
									<Grid item xs={6}>
										<Box sx={{ textAlign: "center" }}>
											<Box
												sx={{
													width: 80,
													height: 80,
													mx: "auto",
													mb: 1,
													borderRadius: "50%",
													background:
														"linear-gradient(135deg, #8DC4FF 0%, #6DAEFF 100%)",
													display: "flex",
													alignItems: "center",
													justifyContent: "center",
													boxShadow: "0 4px 20px rgba(141, 196, 255, 0.3)",
												}}
											>
												<Box>
													<Typography
														variant="h5"
														fontWeight={700}
														color="white"
													>
														{Math.round(
															results.optimal_staking_levels.sol * 100,
														)}
														%
													</Typography>
													<Typography
														variant="caption"
														color="white"
														fontWeight={500}
														sx={{ fontSize: "0.7rem" }}
													>
														SOL
													</Typography>
												</Box>
											</Box>
											<Typography
												variant="caption"
												color="text.secondary"
												sx={{ fontSize: "0.75rem" }}
											>
												Solana Optimal Level
											</Typography>
										</Box>
									</Grid>
								</Grid>
							</Box>
						</Grid>
					</Grid>
				</Box>
			</GlassCard>

			{/* Sensitivity Analysis 3D Surfaces */}
			<GlassCard>
				<Box p={2}>
					<Typography variant="h6" sx={{ mb: 2, ...glassStyles.gradientText }}>
						Sensitivity Analysis - 3D Surfaces
					</Typography>

					{results.sensitivity_analysis_2d &&
					ethLevels.length > 0 &&
					solLevels.length > 0 ? (
						<Grid container spacing={1}>
							<Grid item xs={12} xl={6}>
								<Typography
									variant="subtitle1"
									sx={{
										mb: 1,
										textAlign: "center",
										fontWeight: 600,
										color: "#6DAEFF",
									}}
								>
									Tracking Error Surface
								</Typography>
								<Box
									sx={{
										height: { xs: 500, md: 600, lg: 650, xl: 700 },
										px: 0,
										borderRadius: 2,
										overflow: "hidden",
										boxShadow: "0 4px 20px rgba(0,0,0,0.3)",
										position: "relative",
										isolation: "isolate",
										zIndex: 1,
									}}
								>
									<Plot
										data={[
											{
												type: "surface",
												x: solLevels,
												y: ethLevels,
												z: teValues,
												colorscale: [
													[0, "#4A94E6"],
													[0.5, "#6DAEFF"],
													[1, "#EF4444"],
												],
												colorbar: {
													title: { text: "TE (%)", font: { size: 14 } },
													tickfont: { color: "#fff", size: 12 },
													thickness: 15,
													len: 0.8,
													x: 1.01,
													y: 0.5,
												},
												hovertemplate:
													"ETH: %{y}%<br>" +
													"SOL: %{x}%<br>" +
													"TE: %{z:.3f}%<br>" +
													"<extra></extra>",
											},
										]}
										layout={{
											paper_bgcolor: "transparent",
											plot_bgcolor: "transparent",
											autosize: true,
											margin: { l: 20, r: 10, b: 40, t: 10 },
											scene: {
												xaxis: {
													title: { text: "Staked SOL (%)", font: { size: 14 } },
													tickfont: { color: "#fff", size: 12 },
													gridcolor: "rgba(109,174,255,0.1)",
													zerolinecolor: "rgba(109,174,255,0.2)",
													showspikes: false,
													tickvals: [70, 75, 80, 85, 90, 95, 100],
													ticktext: [
														"70%",
														"75%",
														"80%",
														"85%",
														"90%",
														"95%",
														"100%",
													],
												},
												yaxis: {
													title: { text: "Staked ETH (%)", font: { size: 14 } },
													tickfont: { color: "#fff", size: 12 },
													gridcolor: "rgba(109,174,255,0.1)",
													zerolinecolor: "rgba(109,174,255,0.2)",
													showspikes: false,
													tickvals: [70, 75, 80, 85, 90, 95, 100],
													ticktext: [
														"70%",
														"75%",
														"80%",
														"85%",
														"90%",
														"95%",
														"100%",
													],
												},
												zaxis: {
													title: {
														text: "Tracking Error (%)",
														font: { size: 14 },
													},
													tickfont: { color: "#fff", size: 12 },
													gridcolor: "rgba(109,174,255,0.1)",
													zerolinecolor: "rgba(109,174,255,0.2)",
													showspikes: false,
												},
												bgcolor: "transparent",
												camera: {
													eye: { x: -1.5, y: -1.5, z: 1.5 },
													center: { x: 0, y: 0, z: 0 },
												},
												aspectmode: "manual",
												aspectratio: { x: 1, y: 1, z: 0.7 },
											},
											font: { color: "#fff" },
											hovermode: "closest",
											dragmode: "orbit",
										}}
										config={{
											responsive: true,
											displayModeBar: "hover",
											displaylogo: false,
											modeBarButtonsToRemove: [
												"toImage",
												"sendDataToCloud",
												"hoverClosest3d",
												"tableRotation",
												"resetCameraDefault3d",
											],
											scrollZoom: true,
											doubleClick: "reset+autosize",
										}}
										style={{ width: "100%", height: "100%" }}
									/>
								</Box>
							</Grid>

							<Grid item xs={12} xl={6}>
								<Typography
									variant="subtitle1"
									sx={{
										mb: 1,
										textAlign: "center",
										fontWeight: 600,
										color: "#10B981",
									}}
								>
									Net Benefit Surface
								</Typography>
								<Box
									sx={{
										height: { xs: 500, md: 600, lg: 650, xl: 700 },
										px: 0,
										borderRadius: 2,
										overflow: "hidden",
										boxShadow: "0 4px 20px rgba(0,0,0,0.3)",
										position: "relative",
										isolation: "isolate",
										zIndex: 1,
									}}
								>
									<Plot
										data={[
											{
												type: "surface",
												x: solLevels,
												y: ethLevels,
												z: netBenefitValues,
												colorscale: [
													[0, "#EF4444"],
													[0.5, "#F59E0B"],
													[1, "#10B981"],
												],
												colorbar: {
													title: {
														text: "Net Benefit (%)",
														font: { size: 14 },
													},
													tickfont: { color: "#fff", size: 12 },
													thickness: 15,
													len: 0.8,
													x: 1.01,
													y: 0.5,
												},
												hovertemplate:
													"ETH: %{y}%<br>" +
													"SOL: %{x}%<br>" +
													"Net Benefit: %{z:.3f}%<br>" +
													"<extra></extra>",
											},
										]}
										layout={{
											paper_bgcolor: "transparent",
											plot_bgcolor: "transparent",
											autosize: true,
											margin: { l: 20, r: 10, b: 40, t: 10 },
											scene: {
												xaxis: {
													title: { text: "Staked SOL (%)", font: { size: 14 } },
													tickfont: { color: "#fff", size: 12 },
													gridcolor: "rgba(109,174,255,0.1)",
													zerolinecolor: "rgba(109,174,255,0.2)",
													showspikes: false,
													tickvals: [70, 75, 80, 85, 90, 95, 100],
													ticktext: [
														"70%",
														"75%",
														"80%",
														"85%",
														"90%",
														"95%",
														"100%",
													],
												},
												yaxis: {
													title: { text: "Staked ETH (%)", font: { size: 14 } },
													tickfont: { color: "#fff", size: 12 },
													gridcolor: "rgba(109,174,255,0.1)",
													zerolinecolor: "rgba(109,174,255,0.2)",
													showspikes: false,
													tickvals: [70, 75, 80, 85, 90, 95, 100],
													ticktext: [
														"70%",
														"75%",
														"80%",
														"85%",
														"90%",
														"95%",
														"100%",
													],
												},
												zaxis: {
													title: {
														text: "Net Benefit (%)",
														font: { size: 14 },
													},
													tickfont: { color: "#fff", size: 12 },
													gridcolor: "rgba(109,174,255,0.1)",
													zerolinecolor: "rgba(109,174,255,0.2)",
													showspikes: false,
												},
												bgcolor: "transparent",
												camera: {
													eye: { x: -1.5, y: -1.5, z: 1.5 },
													center: { x: 0, y: 0, z: 0 },
												},
												aspectmode: "manual",
												aspectratio: { x: 1, y: 1, z: 0.7 },
											},
											font: { color: "#fff" },
											hovermode: "closest",
											dragmode: "orbit",
										}}
										config={{
											responsive: true,
											displayModeBar: "hover",
											displaylogo: false,
											modeBarButtonsToRemove: [
												"toImage",
												"sendDataToCloud",
												"hoverClosest3d",
												"tableRotation",
												"resetCameraDefault3d",
											],
											scrollZoom: true,
											doubleClick: "reset+autosize",
										}}
										style={{ width: "100%", height: "100%" }}
									/>
								</Box>
							</Grid>
						</Grid>
					) : (
						<Box textAlign="center" py={4}>
							<Typography variant="body1" color="text.secondary">
								3D sensitivity analysis data not available. Please recalculate.
							</Typography>
						</Box>
					)}
				</Box>
			</GlassCard>

			{/* Tracking Error Decomposition & Yield Benefits */}
			<Box>
				<Grid container spacing={2}>
					{/* Tracking Error Decomposition Card */}
					<Grid item xs={12} lg={4}>
						<GlassCard
							sx={{
								height: "100%",
								position: "relative",
								isolation: "isolate",
							}}
						>
							<Box p={2}>
								<Typography
									variant="subtitle1"
									sx={{ mb: 1.5, fontWeight: 600, color: "#6DAEFF" }}
								>
									Tracking Error Decomposition
								</Typography>

								{/* Waterfall Chart */}
								<Box
									sx={{
										height: 280,
										position: "relative",
										overflow: "hidden",
										zIndex: 1,
										"& .js-plotly-plot": {
											position: "relative",
											zIndex: 1,
										},
										"& .plotly": {
											position: "relative",
											zIndex: 1,
										},
									}}
								>
									<Plot
										data={[
											{
												type: "waterfall" as any,
												orientation: "v",
												measure: [
													"relative",
													"relative",
													"relative",
													"total",
												] as any,
												x: ["ETH", "SOL", "Cross-Asset", "Total"],
												textposition: "outside" as any,
												text: [
													`${(results.decomposition.te_eth_only * 100).toFixed(3)}%`,
													`${(results.decomposition.te_sol_only * 100).toFixed(3)}%`,
													`${((results.decomposition.tracking_error - Math.sqrt(results.decomposition.te_eth_only ** 2 + results.decomposition.te_sol_only ** 2)) * 100).toFixed(3)}%`,
													`${(results.decomposition.tracking_error * 100).toFixed(3)}%`,
												],
												y: [
													results.decomposition.te_eth_only * 100,
													results.decomposition.te_sol_only * 100,
													(results.decomposition.tracking_error -
														Math.sqrt(
															results.decomposition.te_eth_only ** 2 +
																results.decomposition.te_sol_only ** 2,
														)) *
														100,
													results.decomposition.tracking_error * 100,
												],
												connector: {
													line: {
														color: "rgba(109, 174, 255, 0.3)",
														dash: "dot",
														width: 2,
													},
												} as any,
												increasing: {
													marker: {
														color: "rgba(109, 174, 255, 0.8)",
														line: {
															color: "rgba(109, 174, 255, 1)",
															width: 1,
														},
													},
												} as any,
												totals: {
													marker: {
														color: "#4A94E6",
														line: {
															color: "#4A94E6",
															width: 2,
														},
													},
												} as any,
												hovertemplate:
													"%{x}<br>Tracking Error: %{y:.3f}%<br>Contribution: %{customdata}%<extra></extra>",
												customdata: [
													results.decomposition.eth_contribution_pct.toFixed(1),
													results.decomposition.sol_contribution_pct.toFixed(1),
													results.decomposition.cross_contribution_pct.toFixed(
														1,
													),
													"100.0",
												],
											} as any,
										]}
										layout={{
											paper_bgcolor: "transparent",
											plot_bgcolor: "transparent",
											autosize: true,
											margin: { l: 50, r: 20, b: 40, t: 10 },
											xaxis: {
												title: {
													text: "Component",
													font: { size: 12, color: "#fff" },
												},
												tickfont: { color: "#fff", size: 11 },
												gridcolor: "rgba(109,174,255,0.1)",
												zerolinecolor: "rgba(109,174,255,0.2)",
											},
											yaxis: {
												title: {
													text: "Tracking Error (%)",
													font: { size: 12, color: "#fff" },
												},
												tickfont: { color: "#fff", size: 11 },
												gridcolor: "rgba(109,174,255,0.1)",
												zerolinecolor: "rgba(109,174,255,0.2)",
												tickformat: ".3f",
												range: [
													0,
													results.decomposition.tracking_error * 100 * 1.75,
												],
											},
											font: { color: "#fff" },
											showlegend: false,
											hoverlabel: {
												bgcolor: "rgba(0,0,0,0.8)",
												bordercolor: "rgba(109,174,255,0.5)",
												font: { color: "#fff" },
											},
										}}
										config={{
											responsive: true,
											displayModeBar: false,
										}}
										style={{ width: "100%", height: "100%" }}
									/>
								</Box>
							</Box>
						</GlassCard>
					</Grid>

					{/* Yield Benefits Card */}
					<Grid item xs={12} lg={8}>
						<GlassCard sx={{ height: "100%" }}>
							<Box p={2}>
								<Typography
									variant="subtitle1"
									sx={{ mb: 1.5, fontWeight: 600, color: "#10B981" }}
								>
									Yield Benefits
								</Typography>

								<TableContainer>
									<Table size="small">
										<TableHead>
											<TableRow>
												<TableCell
													sx={{
														color: "#fff",
														borderBottom: "2px solid rgba(109,174,255,0.2)",
														fontWeight: 600,
													}}
												>
													Component
												</TableCell>
												<TableCell
													align="right"
													sx={{
														color: "#6DAEFF",
														borderBottom: "2px solid rgba(109,174,255,0.2)",
														fontWeight: 600,
													}}
												>
													ETH
												</TableCell>
												<TableCell
													align="right"
													sx={{
														color: "#8DC4FF",
														borderBottom: "2px solid rgba(109,174,255,0.2)",
														fontWeight: 600,
													}}
												>
													SOL
												</TableCell>
											</TableRow>
										</TableHead>
										<TableBody>
											<TableRow>
												<TableCell
													sx={{
														color: "rgba(255,255,255,0.8)",
														borderBottom: "1px solid rgba(109,174,255,0.1)",
													}}
												>
													Baseline Benefit
												</TableCell>
												<TableCell
													align="right"
													sx={{
														color: "#fff",
														borderBottom: "1px solid rgba(109,174,255,0.1)",
													}}
												>
													<Box>
														<Box>
															{(
																results.net_benefit.eth_benefit_baseline * 100
															).toFixed(3)}
															%
														</Box>
														<Box
															sx={{
																fontSize: "0.875rem",
																color: "rgba(255,255,255,0.6)",
															}}
														>
															{formatCurrency(
																calculateDollarValue(
																	results.net_benefit.eth_benefit_baseline,
																),
															)}
														</Box>
													</Box>
												</TableCell>
												<TableCell
													align="right"
													sx={{
														color: "#fff",
														borderBottom: "1px solid rgba(109,174,255,0.1)",
													}}
												>
													<Box>
														<Box>
															{(
																results.net_benefit.sol_benefit_baseline * 100
															).toFixed(3)}
															%
														</Box>
														<Box
															sx={{
																fontSize: "0.875rem",
																color: "rgba(255,255,255,0.6)",
															}}
														>
															{formatCurrency(
																calculateDollarValue(
																	results.net_benefit.sol_benefit_baseline,
																),
															)}
														</Box>
													</Box>
												</TableCell>
											</TableRow>
											<TableRow>
												<TableCell
													sx={{
														color: "rgba(255,255,255,0.8)",
														borderBottom: "1px solid rgba(109,174,255,0.1)",
													}}
												>
													Marginal Benefit
												</TableCell>
												<TableCell
													align="right"
													sx={{
														color: "#fff",
														borderBottom: "1px solid rgba(109,174,255,0.1)",
													}}
												>
													<Box>
														<Box>
															{(
																results.net_benefit.eth_benefit_marginal * 100
															).toFixed(3)}
															%
														</Box>
														<Box
															sx={{
																fontSize: "0.875rem",
																color: "rgba(255,255,255,0.6)",
															}}
														>
															{formatCurrency(
																calculateDollarValue(
																	results.net_benefit.eth_benefit_marginal,
																),
															)}
														</Box>
													</Box>
												</TableCell>
												<TableCell
													align="right"
													sx={{
														color: "#fff",
														borderBottom: "1px solid rgba(109,174,255,0.1)",
													}}
												>
													<Box>
														<Box>
															{(
																results.net_benefit.sol_benefit_marginal * 100
															).toFixed(3)}
															%
														</Box>
														<Box
															sx={{
																fontSize: "0.875rem",
																color: "rgba(255,255,255,0.6)",
															}}
														>
															{formatCurrency(
																calculateDollarValue(
																	results.net_benefit.sol_benefit_marginal,
																),
															)}
														</Box>
													</Box>
												</TableCell>
											</TableRow>
											<TableRow>
												<TableCell
													sx={{
														color: "#fff",
														fontWeight: 600,
														borderBottom: "none",
														borderTop: "2px solid rgba(109,174,255,0.2)",
													}}
												>
													Total
												</TableCell>
												<TableCell
													align="right"
													sx={{
														color: "#6DAEFF",
														fontWeight: 600,
														borderBottom: "none",
														borderTop: "2px solid rgba(109,174,255,0.2)",
													}}
												>
													<Box>
														<Box>
															{(
																results.net_benefit.eth_benefit_total * 100
															).toFixed(3)}
															%
														</Box>
														<Box
															sx={{
																fontSize: "0.875rem",
																color: "rgba(255,255,255,0.6)",
															}}
														>
															{formatCurrency(
																calculateDollarValue(
																	results.net_benefit.eth_benefit_total,
																),
															)}
														</Box>
													</Box>
												</TableCell>
												<TableCell
													align="right"
													sx={{
														color: "#8DC4FF",
														fontWeight: 600,
														borderBottom: "none",
														borderTop: "2px solid rgba(109,174,255,0.2)",
													}}
												>
													<Box>
														<Box>
															{(
																results.net_benefit.sol_benefit_total * 100
															).toFixed(3)}
															%
														</Box>
														<Box
															sx={{
																fontSize: "0.875rem",
																color: "rgba(255,255,255,0.6)",
															}}
														>
															{formatCurrency(
																calculateDollarValue(
																	results.net_benefit.sol_benefit_total,
																),
															)}
														</Box>
													</Box>
												</TableCell>
											</TableRow>
										</TableBody>
									</Table>
								</TableContainer>

								<Box
									sx={{
										mt: 2,
										pt: 1.5,
										borderTop: "1px solid rgba(109,174,255,0.2)",
									}}
								>
									<Box
										sx={{
											display: "flex",
											justifyContent: "space-between",
											alignItems: "baseline",
										}}
									>
										<Typography
											variant="body2"
											sx={{ color: "rgba(255,255,255,0.8)", fontWeight: 500 }}
										>
											Combined Yield Benefit
										</Typography>
										<Box sx={{ textAlign: "right" }}>
											<Typography
												variant="body1"
												sx={{ fontWeight: 600, color: "#10B981" }}
											>
												{(
													results.net_benefit.total_yield_benefit * 100
												).toFixed(3)}
												%
											</Typography>
											<Typography
												sx={{
													fontSize: "0.875rem",
													color: "rgba(255,255,255,0.6)",
												}}
											>
												{formatCurrency(
													calculateDollarValue(
														results.net_benefit.total_yield_benefit,
													),
												)}
											</Typography>
										</Box>
									</Box>
								</Box>
							</Box>
						</GlassCard>
					</Grid>
				</Grid>
			</Box>
		</Stack>
	);
};
