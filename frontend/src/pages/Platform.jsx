import { PlatformView } from '../components/platform'
import { withOnboardingDoneRequired } from '../hocs/withOnboardingDoneRequired'

function Platform() {
  return <PlatformView />
}

export default withOnboardingDoneRequired(Platform)
