import {BrowserRouter as Router, Route, Routes} from "react-router-dom";
import { AuthProvider } from './contexts/AuthContext';
import Home from './pages/Home.tsx'

function App() {
	return (
		<AuthProvider>
			<Router>
				<div className="min-h-screen bg-neutral-900">
					<Routes>
						<Route path="/" element={<Home />}/>
					</Routes>
				</div>
			</Router>
		</AuthProvider>
	)
}

export default App;