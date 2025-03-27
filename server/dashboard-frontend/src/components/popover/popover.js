import {
  useFloating,
  autoUpdate,
  offset,
  flip,
  shift,
  useClick,
  useDismiss,
  useRole,
  useInteractions,
  FloatingFocusManager
} from '@floating-ui/react';
import { isMobile, useMobileOrientation } from "react-device-detect";
import { theme } from '../../styles/theme';

export const Popover = function({ reference_element, is_open, set_is_open, children, placement, offset_opts, style }) {
	const { isLandscape } = useMobileOrientation();

	const default_placement = isMobile && isLandscape ? "right-end" : "right-start";
	const default_cross_axis = isMobile && isLandscape ? 16 : -16;

	const {refs, floatingStyles, context} = useFloating({
		open: is_open,
		onOpenChange: set_is_open,
		placement: placement || default_placement,
		middleware: [offset(offset_opts || {mainAxis: 8, crossAxis: default_cross_axis }), flip(), shift()],
		whileElementsMounted: autoUpdate,
	});

	const click = useClick(context);
	const dismiss = useDismiss(context);
	const role = useRole(context);

	const {getReferenceProps, getFloatingProps} = useInteractions([
		click,
		dismiss,
		role,
	]);

	return (<>
		<div ref={refs.setReference} {...getReferenceProps()}>
			{reference_element}
		</div>
		{is_open && (
			<FloatingFocusManager context={context} modal={false}>
				<div
					ref={refs.setFloating}
					style={{ ...floatingStyles, zIndex: theme.z_index.popover, ...style }}
					{...getFloatingProps()}
				>
					{children}
				</div>
			</FloatingFocusManager>
		)}
	</>);
}
