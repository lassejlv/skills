//! Small, dependency-free spring helpers for GPUI interaction work.
//!
//! Copy this into the target crate, adapt its scalar type and timing source,
//! and drive it only while motion is active. This file deliberately contains
//! no GPUI API so the math can be unit-tested independently of a pinned GPUI
//! revision.

/// A damped spring described in product-friendly terms.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct SpringConfig {
    /// Approximate seconds for the response to settle.
    pub response: f32,
    /// Damping ratio: 1.0 is critically damped, below 1.0 can overshoot.
    pub damping_ratio: f32,
    /// Absolute position threshold used by `Spring1D::is_settled`.
    pub position_epsilon: f32,
    /// Absolute velocity threshold used by `Spring1D::is_settled`.
    pub velocity_epsilon: f32,
}

impl Default for SpringConfig {
    fn default() -> Self {
        Self {
            response: 0.36,
            damping_ratio: 0.88,
            position_epsilon: 0.001,
            velocity_epsilon: 0.001,
        }
    }
}

/// One-dimensional spring state. Use one instance per independently animated
/// scalar, or wrap multiple instances for points, sizes, and color channels.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Spring1D {
    pub value: f32,
    pub velocity: f32,
    pub target: f32,
}

impl Spring1D {
    pub const fn new(value: f32) -> Self {
        Self {
            value,
            velocity: 0.0,
            target: value,
        }
    }

    /// Retarget without resetting velocity. This keeps interruption continuous.
    pub fn retarget(&mut self, target: f32) {
        self.target = target;
    }

    /// Snap immediately. Use for reduced motion or discontinuous state changes.
    pub fn snap_to(&mut self, value: f32) {
        self.value = value;
        self.velocity = 0.0;
        self.target = value;
    }

    pub fn is_settled(&self, config: SpringConfig) -> bool {
        (self.target - self.value).abs() <= config.position_epsilon
            && self.velocity.abs() <= config.velocity_epsilon
    }

    /// Advance using capped, semi-implicit Euler substeps.
    ///
    /// Feed elapsed wall-clock time in seconds. Capping and subdividing a late
    /// frame keeps the spring finite and predictable after debugger pauses or
    /// temporary stalls. Return `true` while another animation frame is needed.
    pub fn step(&mut self, elapsed_seconds: f32, config: SpringConfig) -> bool {
        if self.is_settled(config) {
            self.snap_to(self.target);
            return false;
        }

        let response = config.response.max(0.001);
        let damping_ratio = config.damping_ratio.max(0.0);
        let omega = std::f32::consts::TAU / response;
        let stiffness = omega * omega;
        let damping = 2.0 * damping_ratio * omega;

        let mut remaining = elapsed_seconds.clamp(0.0, 0.1);
        const MAX_STEP: f32 = 1.0 / 120.0;
        while remaining > 0.0 {
            let dt = remaining.min(MAX_STEP);
            let displacement = self.value - self.target;
            let acceleration = -stiffness * displacement - damping * self.velocity;
            self.velocity += acceleration * dt;
            self.value += self.velocity * dt;
            remaining -= dt;
        }

        if self.is_settled(config) {
            self.snap_to(self.target);
            false
        } else {
            true
        }
    }
}

/// Project a release using exponential velocity decay.
///
/// `deceleration_rate` is the velocity retained per second and must be between
/// zero and one. Keep projection bounded by the component's semantic limits.
pub fn projected_position(position: f32, velocity: f32, deceleration_rate: f32) -> f32 {
    let rate = deceleration_rate.clamp(0.000_001, 0.999_999);
    position - velocity / rate.ln()
}

/// Apply diminishing resistance after dragging past a boundary.
pub fn rubber_band(overshoot: f32, dimension: f32, coefficient: f32) -> f32 {
    if overshoot == 0.0 || dimension <= 0.0 {
        return 0.0;
    }

    let sign = overshoot.signum();
    let distance = overshoot.abs();
    let scaled = (coefficient.max(0.0) * distance * dimension)
        / (dimension + coefficient.max(0.0) * distance);
    sign * scaled
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn spring_converges() {
        let config = SpringConfig::default();
        let mut spring = Spring1D::new(0.0);
        spring.retarget(1.0);

        for _ in 0..600 {
            spring.step(1.0 / 120.0, config);
        }

        assert!(spring.is_settled(config));
        assert_eq!(spring.value, 1.0);
        assert_eq!(spring.velocity, 0.0);
    }

    #[test]
    fn retarget_preserves_velocity() {
        let config = SpringConfig::default();
        let mut spring = Spring1D::new(0.0);
        spring.retarget(1.0);
        spring.step(1.0 / 60.0, config);
        let velocity = spring.velocity;

        spring.retarget(-1.0);

        assert_eq!(spring.velocity, velocity);
    }

    #[test]
    fn late_frames_stay_finite() {
        let mut spring = Spring1D::new(0.0);
        spring.retarget(1.0);
        spring.step(60.0, SpringConfig::default());

        assert!(spring.value.is_finite());
        assert!(spring.velocity.is_finite());
    }

    #[test]
    fn rubber_band_is_bounded_and_symmetric() {
        let positive = rubber_band(1000.0, 200.0, 0.55);
        let negative = rubber_band(-1000.0, 200.0, 0.55);

        assert!(positive < 200.0);
        assert_eq!(positive, -negative);
    }

    #[test]
    fn projection_follows_velocity() {
        assert!(projected_position(10.0, 100.0, 0.9) > 10.0);
        assert!(projected_position(10.0, -100.0, 0.9) < 10.0);
    }
}
