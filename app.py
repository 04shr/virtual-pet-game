from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                            QSlider, QTextEdit, QPushButton, QFrame, QProgressBar,
                            QScrollArea, QSizePolicy)
from PyQt5.QtCore import QTimer, Qt, QPropertyAnimation, QRect
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette, QBrush, QImage, QFontDatabase
import sys, random, os, time

class StoryScene:
    def __init__(self, title, content, options=None):
        self.title = title
        self.content = content
        self.options = options if options else []

class VirtualPetGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌈 A Magical Pet Journey 🌈")
        self.setGeometry(100, 100, 900, 700)
        
        # Set background color with a subtle pattern
        self.setStyleSheet("""
            QWidget {
                background-color: #FFF5E1;
                font-family: 'Comic Sans MS', cursive;
            }
            QPushButton {
                background-color: #FFD6A5;
                border: 2px solid #FF9A5A;
                border-radius: 15px;
                padding: 10px;
                color: #6A4B35;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFAA5A;
            }
            QProgressBar {
                border: 2px solid #8EC3B0;
                border-radius: 10px;
                text-align: center;
                background-color: #FAFAFA;
            }
            QProgressBar::chunk {
                background-color: #8EC3B0;
                border-radius: 8px;
            }
            QTextEdit {
                border: 3px solid #FFB6B9;
                border-radius: 15px;
                padding: 10px;
                background-color: #FFEFD5;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        # Pet attributes
        self.pet_name = ""
        self.pet_type = ""
        self.hunger = 50
        self.cleanliness = 50
        self.energy = 50
        self.happiness = 50
        self.days_with_pet = 0
        
        # Action tracking
        self.bath_count = 0
        self.sleep_count = 0
        self.last_feed_time = 0

        # Initialize progress bar attributes to None
        self.hunger_bar = None
        self.clean_bar = None
        self.energy_bar = None
        self.happy_bar = None
        self.pet_selected = False

        # Story elements
        self.current_story = None
        self.story_scenes = self.create_story_scenes()
        
        # Pet choices with enhanced descriptions
        self.pet_choices = {
            "Dinno": ("dino.webp", "A playful little dinosaur with sparkling eyes! Dinno loves adventures and warm cuddles. Legend says Dinno's ancestors were magical creatures who protected the ancient forests. 🦖"),
            "Monkey": ("monkey.webp", "A mischievous monkey with a heart of gold! Monkey enjoys swinging from magical vines and collecting shiny treasures. He's known for his contagious laughter that brings joy to everyone. 🐵"),
            "Hippo": ("hippo.png", "A gentle hippo with dreams as big as the ocean! Hippo loves splashing in enchanted waters and making rainbow bubbles. She has a secret talent for dancing under the moonlight. 🦛")
        }

        # Create a scroll area for responsive design
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Main container widget for scroll area
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Set the container as the scroll area's widget
        self.scroll_area.setWidget(self.container)
        
        # Main layout for the application
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scroll_area)
        
        # Initialize UI
        self.initUI()

        # Timers for gradual status decrease and alerts
        self.timer = QTimer()
        self.timer.timeout.connect(self.decrease_happiness)
        self.timer.start(12000)  # Slower decrease (was 5000)
        
        self.alert_timer = QTimer()
        self.alert_timer.timeout.connect(self.show_alerts)
        self.alert_timer.start(60000)  # Check alerts every minute
        
        # Random events timer
        self.event_timer = QTimer()
        self.event_timer.timeout.connect(self.random_event)
        self.event_timer.start(120000)  # Every 2 minutes
        
        # Day counter timer
        self.day_timer = QTimer()
        self.day_timer.timeout.connect(self.new_day)
        self.day_timer.start(300000)  # Every 5 minutes is a new day

    def create_story_scenes(self):
        return {
            "intro": StoryScene(
                "The Beginning of a Magical Journey",
                "In the mystical land of Petopia, where dreams come to life and magic fills the air, "
                "a special creature awaits a friend like you! 🌟\n\n"
                "The wise guardian of Petopia has sensed your kind heart and has invited you to choose "
                "a magical companion who will grow alongside you. \n\n"
                "Who will you choose to join you on this adventure?"
            ),
            "selected": StoryScene(
                "A New Friendship Begins",
                "As you extend your hand, a warm glow surrounds you and your new friend! "
                "The bond of friendship begins to form, creating a magical connection between your hearts. ✨\n\n"
                "The guardian smiles and whispers: \"Take good care of your companion. "
                "Feed them when hungry, keep them clean, and ensure they get proper rest. "
                "Your journey together will be filled with wonder and joy!\""
            )
        }

    def initUI(self):
        # Title with fancy font
        self.title_label = QLabel("🌈 A Magical Pet Journey 🌈")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 28px; color: #FF6B6B; font-weight: bold; margin: 10px;")
        self.layout.addWidget(self.title_label)
        
        # Decorative line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #FFB6B9; margin: 0 50px;")
        self.layout.addWidget(line)
        
        # Story text with beautiful styling
        self.story_text = QTextEdit(self)
        self.story_text.setReadOnly(True)
        self.story_text.setFont(QFont("Comic Sans MS", 12))
        self.story_text.setMinimumHeight(150)
        self.layout.addWidget(self.story_text)
        
        # Start with intro story
        self.current_story = "intro"
        self.display_story()
        
        # Container for pet selection to maintain center alignment
        pet_selection_container = QWidget()
        pet_selection_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.pet_selection_layout = QHBoxLayout(pet_selection_container)
        self.pet_selection_layout.setAlignment(Qt.AlignCenter)
        self.pet_selection_layout.setSpacing(20)
        
        for pet, (img_path, desc) in self.pet_choices.items():
            pet_frame = QFrame()
            pet_frame.setFixedWidth(200)  # Fixed width for consistent sizing
            pet_frame.setStyleSheet("""
                QFrame {
                    background-color: #D4F0F0;
                    border: 3px solid #8EC3B0;
                    border-radius: 20px;
                    padding: 10px;
                }
                QFrame:hover {
                    background-color: #A8E6CF;
                    border: 3px solid #3D7EA6;
                }
            """)
            pet_layout = QVBoxLayout(pet_frame)
            
            pet_name_label = QLabel(pet)
            pet_name_label.setAlignment(Qt.AlignCenter)
            pet_name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #3D7EA6;")
            pet_layout.addWidget(pet_name_label)
            
            pet_widget = QLabel()
            pet_img = QPixmap(img_path).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            pet_widget.setPixmap(pet_img)
            pet_widget.setAlignment(Qt.AlignCenter)
            pet_layout.addWidget(pet_widget)
            
            # Short description
            desc_label = QLabel(desc.split("!")[0] + "!")
            desc_label.setWordWrap(True)
            desc_label.setAlignment(Qt.AlignCenter)
            desc_label.setStyleSheet("font-size: 12px; color: #5E6472; margin: 5px;")
            pet_layout.addWidget(desc_label)
            
            # Make whole frame clickable
            pet_frame.mousePressEvent = lambda event, pet=pet, img=img_path, desc=desc: self.select_pet(pet, img, desc)
            
            self.pet_selection_layout.addWidget(pet_frame)
        
        self.layout.addWidget(pet_selection_container)

    def display_story(self):
        scene = self.story_scenes.get(self.current_story)
        if scene:
            styled_text = f"<h2 style='color: #FF6B6B; text-align: center;'>{scene.title}</h2>"
            styled_text += f"<p style='font-size: 14px; line-height: 1.5;'>{scene.content}</p>"
            self.story_text.setHtml(styled_text)

    def select_pet(self, pet, img_path, desc):
        self.pet_type = pet
        self.pet_name = pet
        
        # Clear pet selection layout
        for i in reversed(range(self.pet_selection_layout.count())):
            widget = self.pet_selection_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Remove pet selection container
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if isinstance(widget, QWidget) and hasattr(widget, 'layout') and widget.layout() == self.pet_selection_layout:
                widget.setParent(None)
                break
        
        # Update story
        self.current_story = "selected"
        self.display_story()
        
        # Create responsive pet display area
        pet_display = QFrame()
        pet_display.setStyleSheet("""
            QFrame {
                background-color: #A8E6CF;
                border: 3px solid #8EC3B0;
                border-radius: 20px;
                padding: 10px;
                margin: 10px 0px;
            }
        """)
        pet_layout = QVBoxLayout(pet_display)
        
        # Center container for pet image and info
        pet_center_widget = QWidget()
        pet_center_layout = QHBoxLayout(pet_center_widget)
        pet_center_layout.setAlignment(Qt.AlignCenter)
        
        # Pet image with animation effect
        self.pet_img_label = QLabel(self)
        self.pet_img_label.setPixmap(QPixmap(img_path).scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.pet_img_label.setAlignment(Qt.AlignCenter)
        pet_center_layout.addWidget(self.pet_img_label)
        
        # Pet info container
        pet_info_widget = QWidget()
        pet_info_layout = QVBoxLayout(pet_info_widget)
        
        # Pet name with styling
        name_label = QLabel(f"✨ {self.pet_name} ✨")
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #3D7EA6; margin-top: 5px;")
        pet_info_layout.addWidget(name_label)
        
        # Days counter
        self.days_label = QLabel(f"Days together: {self.days_with_pet}")
        self.days_label.setAlignment(Qt.AlignCenter)
        self.days_label.setStyleSheet("font-size: 14px; color: #5E6472;")
        pet_info_layout.addWidget(self.days_label)
        
        # Add limits information
        limits_label = QLabel("Daily Limits: 2 Baths, 2 Naps")
        limits_label.setAlignment(Qt.AlignCenter)
        limits_label.setStyleSheet("font-size: 12px; color: #FF9A5A;")
        pet_info_layout.addWidget(limits_label)
        
        # Counter for daily activities
        self.activity_count_label = QLabel("Today's activities: 0 baths, 0 naps")
        self.activity_count_label.setAlignment(Qt.AlignCenter)
        self.activity_count_label.setStyleSheet("font-size: 12px; color: #5E6472;")
        pet_info_layout.addWidget(self.activity_count_label)
        
        pet_center_layout.addWidget(pet_info_widget)
        pet_layout.addWidget(pet_center_widget)
        
        self.layout.addWidget(pet_display)
        
        # Stats with cute icons and progress bars
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #FFDFD3;
                border: 3px solid #FFB6B9;
                border-radius: 15px;
                padding: 15px;
                margin: 0;
            }
        """)
        stats_layout = QVBoxLayout(stats_frame)
        
        # Create progress bars for each stat
        hunger_layout = QHBoxLayout()
        hunger_icon = QLabel("🍖")
        hunger_icon.setStyleSheet("font-size: 18px;")
        hunger_layout.addWidget(hunger_icon)
        hunger_layout.addWidget(QLabel("Hunger:"))
        self.hunger_bar = QProgressBar()
        self.hunger_bar.setMaximum(100)
        self.hunger_bar.setValue(self.hunger)
        hunger_layout.addWidget(self.hunger_bar)
        stats_layout.addLayout(hunger_layout)
        
        clean_layout = QHBoxLayout()
        clean_icon = QLabel("🚿")
        clean_icon.setStyleSheet("font-size: 18px;")
        clean_layout.addWidget(clean_icon)
        clean_layout.addWidget(QLabel("Cleanliness:"))
        self.clean_bar = QProgressBar()
        self.clean_bar.setMaximum(100)
        self.clean_bar.setValue(self.cleanliness)
        clean_layout.addWidget(self.clean_bar)
        stats_layout.addLayout(clean_layout)
        
        energy_layout = QHBoxLayout()
        energy_icon = QLabel("💤")
        energy_icon.setStyleSheet("font-size: 18px;")
        energy_layout.addWidget(energy_icon)
        energy_layout.addWidget(QLabel("Energy:"))
        self.energy_bar = QProgressBar()
        self.energy_bar.setMaximum(100)
        self.energy_bar.setValue(self.energy)
        energy_layout.addWidget(self.energy_bar)
        stats_layout.addLayout(energy_layout)
        
        happy_layout = QHBoxLayout()
        happy_icon = QLabel("😊")
        happy_icon.setStyleSheet("font-size: 18px;")
        happy_layout.addWidget(happy_icon)
        happy_layout.addWidget(QLabel("Happiness:"))
        self.happy_bar = QProgressBar()
        self.happy_bar.setMaximum(100)
        self.happy_bar.setValue(self.happiness)
        happy_layout.addWidget(self.happy_bar)
        stats_layout.addLayout(happy_layout)
        
        self.layout.addWidget(stats_frame)
        
        # Overall mood meter
        self.mood_label = QLabel("Current Mood:")
        self.mood_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.mood_label)
        
        # Action buttons with cute icons in a responsive grid
        actions_container = QWidget()
        self.actions_layout = QHBoxLayout(actions_container)
        self.actions_layout.setAlignment(Qt.AlignCenter)
        self.actions_layout.setSpacing(15)
        
        button_width = 150
        
        self.feed_btn = QPushButton("🍖 Feed")
        self.feed_btn.clicked.connect(self.feed_pet)
        self.feed_btn.setMinimumHeight(50)
        self.feed_btn.setFixedWidth(button_width)
        
        self.bathe_btn = QPushButton("🚿 Bathe")
        self.bathe_btn.clicked.connect(self.bathe_pet)
        self.bathe_btn.setMinimumHeight(50)
        self.bathe_btn.setFixedWidth(button_width)
        
        self.sleep_btn = QPushButton("💤 Sleep")
        self.sleep_btn.clicked.connect(self.sleep_pet)
        self.sleep_btn.setMinimumHeight(50)
        self.sleep_btn.setFixedWidth(button_width)
        
        self.play_btn = QPushButton("🎮 Play")
        self.play_btn.clicked.connect(self.play_with_pet)
        self.play_btn.setMinimumHeight(50)
        self.play_btn.setFixedWidth(button_width)
        
        self.actions_layout.addWidget(self.feed_btn)
        self.actions_layout.addWidget(self.bathe_btn)
        self.actions_layout.addWidget(self.sleep_btn)
        self.actions_layout.addWidget(self.play_btn)
        
        self.layout.addWidget(actions_container)
        
        # Set pet_selected to True once all UI elements are created
        self.pet_selected = True
        self.update_stats()

    def update_stats(self):
        # Only update if pet is selected and progress bars exist
        if not self.pet_selected or not self.hunger_bar:
            return
            
        # Update progress bars
        self.hunger_bar.setValue(self.hunger)
        self.clean_bar.setValue(self.cleanliness)
        self.energy_bar.setValue(self.energy)
        self.happy_bar.setValue(self.happiness)
        
        # Update progress bar colors based on values
        self.update_bar_color(self.hunger_bar, self.hunger)
        self.update_bar_color(self.clean_bar, self.cleanliness)
        self.update_bar_color(self.energy_bar, self.energy)
        self.update_bar_color(self.happy_bar, self.happiness)
        
        # Update mood label
        mood_value = (self.hunger + self.cleanliness + self.energy + self.happiness) // 4
        if mood_value > 80:
            mood_text = "Ecstatic! 🤩"
        elif mood_value > 60:
            mood_text = "Happy! 😊"
        elif mood_value > 40:
            mood_text = "Content 🙂"
        elif mood_value > 20:
            mood_text = "Sad 😔"
        else:
            mood_text = "Unhappy 😢"
        
        self.mood_label.setText(f"Current Mood: {mood_text}")
        
        # Update activity count label
        self.activity_count_label.setText(f"Today's activities: {self.bath_count} baths, {self.sleep_count} naps")
        
        # Update button states based on limits
        self.bathe_btn.setEnabled(self.bath_count < 2)
        self.sleep_btn.setEnabled(self.sleep_count < 2)
        
        # Update feed button based on time limit (5-6 hours)
        current_time = time.time()
        feed_cooldown = 18000  # 5 hours in seconds
        self.feed_btn.setEnabled(current_time - self.last_feed_time >= feed_cooldown or self.last_feed_time == 0)
        
        if not self.feed_btn.isEnabled():
            remaining_time = feed_cooldown - (current_time - self.last_feed_time)
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time % 3600) // 60)
            self.feed_btn.setText(f"🍖 Feed ({hours}h {minutes}m)")
        else:
            self.feed_btn.setText("🍖 Feed")

    def update_bar_color(self, bar, value):
        if value > 60:
            bar.setStyleSheet("QProgressBar::chunk { background-color: #77DD77; }")  # Green
        elif value > 30:
            bar.setStyleSheet("QProgressBar::chunk { background-color: #FFD700; }")  # Yellow
        else:
            bar.setStyleSheet("QProgressBar::chunk { background-color: #FF6961; }")  # Red

    def decrease_happiness(self):
        # Only decrease if pet is selected
        if not self.pet_selected:
            return
            
        # Slower decrease rates
        self.hunger = max(0, self.hunger - 1)
        self.cleanliness = max(0, self.cleanliness - 1)
        self.energy = max(0, self.energy - 1)
        
        # Happiness decreases slower
        if random.random() < 0.7:  # 70% chance
            self.happiness = max(0, self.happiness - 1)
            
        self.update_stats()

    def show_alerts(self):
        # Only show alerts if pet is selected
        if not self.pet_selected:
            return
            
        needs = []
        
        if self.hunger < 30:
            needs.append(f"🍖 {self.pet_name}'s tummy is rumbling! A magical feast would be wonderful!")
        
        if self.cleanliness < 30:
            needs.append(f"🚿 Oh my! {self.pet_name} could use a bubbly bath to wash away the day's adventures!")
        
        if self.energy < 30:
            needs.append(f"💤 {self.pet_name}'s eyelids are getting heavy. A cozy nap would be dreamy!")
            
        if self.happiness < 30:
            needs.append(f"🎮 {self.pet_name} looks a bit bored. Some playtime would brighten their day!")
        
        if needs:
            styled_text = "<h3 style='color: #FF6B6B; text-align: center;'>Your Pet Needs You!</h3>"
            styled_text += "<p style='font-size: 14px; line-height: 1.5;'>" + "<br>".join(needs) + "</p>"
            self.story_text.setHtml(styled_text)
    
    def feed_pet(self):
        # Check if enough time has passed (5-6 hours)
        current_time = time.time()
        feed_cooldown = 18000  # 5 hours in seconds
        
        if current_time - self.last_feed_time < feed_cooldown and self.last_feed_time > 0:
            remaining_time = feed_cooldown - (current_time - self.last_feed_time)
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time % 3600) // 60)
            
            styled_text = "<h3 style='color: #FF6B6B; text-align: center;'>Too Soon for Another Meal!</h3>"
            styled_text += f"<p style='font-size: 14px; line-height: 1.5;'>{self.pet_name} isn't hungry yet! The magical nutrients from the last meal are still providing energy. Please wait another {hours} hours and {minutes} minutes before feeding again.</p>"
            self.story_text.setHtml(styled_text)
            return
            
        old_value = self.hunger
        self.hunger = min(100, self.hunger + 25)
        self.happiness = min(100, self.happiness + 10)
        self.last_feed_time = current_time
        
        # Different stories based on hunger level
        if old_value < 30:
            story = f"{self.pet_name}'s eyes light up at the sight of the magical food! With a happy dance and twinkling eyes, your pet devours the meal, letting out a satisfied purr. The food's enchantment brings a warm glow to {self.pet_name}'s cheeks! 🍖✨"
        else:
            story = f"{self.pet_name} nibbles delicately on the magical treats you offer. Each morsel sparkles with enchanted energy that makes your pet's fur shimmer with joy! After finishing, {self.pet_name} nuzzles your hand in gratitude. 🍖💫"
        
        styled_text = "<h3 style='color: #77DD77; text-align: center;'>Feeding Time!</h3>"
        styled_text += f"<p style='font-size: 14px; line-height: 1.5;'>{story}</p>"
        self.story_text.setHtml(styled_text)
        self.update_stats()

    def bathe_pet(self):
        # Check if bath limit reached
        if self.bath_count >= 2:
            styled_text = "<h3 style='color: #FF6B6B; text-align: center;'>Bath Limit Reached!</h3>"
            styled_text += f"<p style='font-size: 14px; line-height: 1.5;'>{self.pet_name} has already had two baths today! Too much bathing can dry out their magical coat. Please wait until tomorrow for another bath.</p>"
            self.story_text.setHtml(styled_text)
            return
            
        old_value = self.cleanliness
        self.cleanliness = min(100, self.cleanliness + 25)
        self.happiness = min(100, self.happiness + 5)
        self.bath_count += 1
        
        # Different stories based on cleanliness level
        if old_value < 30:
            story = f"The enchanted bubbles float around {self.pet_name}, who giggles as they pop and release tiny sparkling stars! The dirt magically dissolves, revealing your pet's beautiful, shiny coat. {self.pet_name} shakes off, sending rainbow droplets dancing through the air! 🚿✨"
        else:
            story = f"{self.pet_name} splashes joyfully in the magical bathwater, creating patterns of light that dance across the surface. The scent of mystic flowers fills the air as your pet enjoys the refreshing sensation of being pampered and loved. 🚿🌸"
        
        styled_text = "<h3 style='color: #73C2FB; text-align: center;'>Bath Time!</h3>"
        styled_text += f"<p style='font-size: 14px; line-height: 1.5;'>{story}</p>"
        self.story_text.setHtml(styled_text)
        self.update_stats()

    def sleep_pet(self):
        # Check if sleep limit reached
        if self.sleep_count >= 2:
            styled_text = "<h3 style='color: #FF6B6B; text-align: center;'>Nap Limit Reached!</h3>"
            styled_text += f"<p style='font-size: 14px; line-height: 1.5;'>{self.pet_name} has already had two naps today! Too much sleep during the day might make it hard for them to rest at night. Try playing instead!</p>"
            self.story_text.setHtml(styled_text)
            return
            
        old_value = self.energy
        self.energy = min(100, self.energy + 25)
        self.happiness = min(100, self.happiness + 5)
        self.sleep_count += 1
        
        # Different stories based on energy level
        if old_value < 30:
            story = f"Exhausted from adventures, {self.pet_name} curls up in the enchanted sleeping nook you prepared. Tiny dream clouds appear above your pet's head, showing visions of magical lands and adventures you'll share tomorrow. {self.pet_name}'s gentle snores create soft melodies in the air. 💤✨"
        else:
            story = f"{self.pet_name} yawns cutely and snuggles into the cozy blanket. As your pet drifts into dreamland, a soft glow surrounds them, and you can hear the faint sounds of lullabies carried by the wind from the fairy forest. 💤🌙"
        
        styled_text = "<h3 style='color: #B19CD9; text-align: center;'>Dreamland Adventures!</h3>"
        styled_text += f"<p style='font-size: 14px; line-height: 1.5;'>{story}</p>"
        self.story_text.setHtml(styled_text)
        self.update_stats()
        
    def play_with_pet(self):
        self.happiness = min(100, self.happiness + 30)
        self.energy = max(0, self.energy - 10)
        
        # Random play activities
        activities = [
            f"{self.pet_name} chases magical floating bubbles that burst into tiny fireworks when touched! With each leap and bound, your pet's eyes shine with pure joy and excitement. 🎮✨",
            f"You and {self.pet_name} explore a miniature enchanted garden that appears from nowhere! The flowers sing sweet melodies as your pet dances through the magical paths. 🎮🌼",
            f"{self.pet_name} discovers a friendly spirit who challenges you both to a game of hide-and-seek among shimmering clouds! Giggles fill the air as you search for your playful companion. 🎮☁️"
        ]
        
        story = random.choice(activities)
        
        styled_text = """<h3 style='color: #FFD700; text-align: center;'>Playtime!</h3>
        <p style='font-size: 14px; line-height: 1.5;'>{story}</p>
        """
        self.story_text.setHtml(styled_text)
        self.update_stats()

    def new_day(self):
        self.days_with_pet += 1
        self.bath_count = 0
        self.sleep_count = 0
        
        self.days_label.setText(f"Days together: {self.days_with_pet}")
        
        styled_text = """
        <h3 style='color: #FFA07A; text-align: center;'>A New Day Begins! ☀️</h3>
        <p style='font-size: 14px; line-height: 1.5;'>
        The sun rises over Petopia, filling the air with warmth and magic! 
        Today is a fresh start for you and {self.pet_name}. 
        What new adventures will unfold?
        </p>
        """
        self.story_text.setHtml(styled_text)
        self.update_stats()

    def random_event(self):
        events = [
            f"A friendly wizard visits and gifts {self.pet_name} a shimmering charm! 🌟", 
            f"A sudden rain of shooting stars fills the sky! {self.pet_name} watches in awe. ✨", 
            f"A mischievous fairy plays a prank on {self.pet_name}, who giggles with joy! 🧚"
        ]
        event = random.choice(events)
        
        styled_text = f"""
        <h3 style='color: #8A2BE2; text-align: center;'>A Magical Event! 🌠</h3>
        <p style='font-size: 14px; line-height: 1.5;'>{event}</p>
        """
        self.story_text.setHtml(styled_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VirtualPetGame()
    window.show()
    sys.exit(app.exec_())
